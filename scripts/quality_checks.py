import duckdb
from utils import DUCKDB_PATH

def main():
    con = duckdb.connect(str(DUCKDB_PATH))
    # 1) id único en staging
    dup = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT id, COUNT(*) c FROM staging.airbnb_listings_clean GROUP BY 1 HAVING COUNT(*)>1
        );
    """).fetchone()[0]
    assert dup == 0, f"Hay {dup} ids duplicados en staging"

    # 2) precios positivos
    neg = con.execute("""
        SELECT COUNT(*) FROM staging.airbnb_listings_clean WHERE price <= 0 OR price IS NULL;
    """).fetchone()[0]
    assert neg == 0, f"Precios inválidos: {neg}"

    # 3) tablas core no vacías
    for t in ["core.dim_host","core.dim_room_type","core.dim_neighbourhood","core.dim_neighbourhood_group","core.fact_listings"]:
        cnt = con.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        assert cnt > 0, f"{t} está vacía"

    con.close()
    print("OK QUALITY CHECKS ✔")

if __name__ == "__main__":
    main()
