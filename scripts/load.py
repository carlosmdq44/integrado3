import duckdb, pandas as pd
from utils import DUCKDB_PATH, RAW_DIR, logging

def latest_raw():
    files = sorted(RAW_DIR.glob("ab_nyc_*.csv"))
    if not files:
        raise FileNotFoundError("No hay archivos en RAW. Corré extract primero.")
    return files[-1]

def main():
    raw_file = latest_raw()
    df = pd.read_csv(raw_file)
    con = duckdb.connect(str(DUCKDB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("DROP TABLE IF EXISTS raw.airbnb_listings;")
    con.register("df_raw", df)
    con.execute("""
        CREATE TABLE raw.airbnb_listings AS
        SELECT * FROM df_raw;
    """)
    con.close()
    logging.info(f"LOAD: {raw_file.name} -> raw.airbnb_listings")
    print("OK LOAD → raw.airbnb_listings")

if __name__ == "__main__":
    main()
