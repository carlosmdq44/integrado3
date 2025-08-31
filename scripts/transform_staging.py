import pandas as pd, numpy as np, duckdb
from utils import DUCKDB_PATH, STAGING_DIR, logging

def winsorize(s: pd.Series, p_low=0.01, p_high=0.99):
    ql, qh = s.quantile([p_low, p_high])
    return s.clip(ql, qh)

def main():
    con = duckdb.connect(str(DUCKDB_PATH))
    # Tomamos RAW a pandas para limpiar en Python:
    df = con.execute("SELECT * FROM raw.airbnb_listings;").df()

    # snake_case
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # tipos
    if "last_review" in df.columns:
        df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")

    num_cols = ["price","minimum_nights","number_of_reviews","reviews_per_month",
                "calculated_host_listings_count","availability_365"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # duplicados por id
    before = len(df)
    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"])
    removed = before - len(df)

    # precio válido y winsor
    if "price" in df.columns:
        df = df[(df["price"].notna()) & (df["price"] > 0)]
        df["price_winsor"] = winsorize(df["price"])

    # proxies
    if "availability_365" in df.columns:
        df["occupancy_proxy"] = 1 - (df["availability_365"].fillna(365) / 365)
    if {"price_winsor","occupancy_proxy"}.issubset(df.columns):
        df["revenue_proxy"] = df["price_winsor"] * df["occupancy_proxy"]

    # guardar staging en DuckDB
    con.execute("CREATE SCHEMA IF NOT EXISTS staging;")
    con.execute("DROP TABLE IF EXISTS staging.airbnb_listings_clean;")
    con.register("df_stg", df)
    con.execute("CREATE TABLE staging.airbnb_listings_clean AS SELECT * FROM df_stg;")
    con.close()

    # opcional CSV de control
    out_csv = STAGING_DIR / "airbnb_listings_clean.csv"
    df.to_csv(out_csv, index=False)

    logging.info(f"STAGING: removed_duplicates={removed}, rows={len(df)}")
    print(f"OK STAGING → staging.airbnb_listings_clean ({len(df)} filas)")

if __name__ == "__main__":
    main()
