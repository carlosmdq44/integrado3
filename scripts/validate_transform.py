# scripts/validate_transform.py
import duckdb

CHECKS = [
    # staging
    ("SELECT COUNT(*)>0 FROM staging.listing_text_features;", True),

    # core
    ("SELECT COUNT(*)>0 FROM core.listing_text_features;", True),
    ("SELECT COUNT(*)>0 FROM core.fact_listings_enriched;", True),

    # gold
    ("SELECT COUNT(*)>0 FROM gold.avg_price_by_area_room;", True),
    ("SELECT COUNT(*)>0 FROM gold.availability_bucket_by_ng;", True),
    ("SELECT COUNT(*)>0 FROM gold.corr_availability_reviews_by_ng;", True),
    ("SELECT COUNT(*)>0 FROM gold.price_vs_text_features;", True),

    # sanidad básica
    ("SELECT MIN(price_winsor)>0 FROM core.fact_listings;", True),
    ("SELECT SUM(has_wifi::INT)+SUM(has_pool::INT) FROM core.listing_text_features;", None),  # solo ejecuta
]

def main():
    con = duckdb.connect("data/warehouse.duckdb")
    for sql, expected in CHECKS:
        got = con.execute(sql).fetchone()[0]
        if expected is True and not got:
            raise AssertionError(f"Falla check: {sql}")
        # expected None -> solo smoke test
    con.close()
    print("OK VALIDATE TRANSFORM ✔")

if __name__ == "__main__":
    main()
