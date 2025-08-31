# scripts/gold.py
import duckdb
from utils import DUCKDB_PATH, GOLD_DIR, logging

QUERIES = {
    "avg_price_by_area": """
SELECT ng.neighbourhood_group, n.neighbourhood,
       AVG(f.price_winsor) AS avg_price
FROM core.fact_listings f
JOIN core.dim_neighbourhood n ON f.n_id = n.n_id
JOIN core.dim_neighbourhood_group ng ON f.ng_id = ng.ng_id
GROUP BY 1,2
ORDER BY avg_price DESC
""",
    "room_type_offer": """
SELECT r.room_type, COUNT(*) AS listings
FROM core.fact_listings f
JOIN core.dim_room_type r ON f.rt_id = r.rt_id
GROUP BY 1 ORDER BY listings DESC
""",
    "room_type_revenue_proxy": """
SELECT r.room_type, AVG(f.revenue_proxy) AS avg_revenue_proxy
FROM core.fact_listings f
JOIN core.dim_room_type r ON f.rt_id = r.rt_id
GROUP BY 1 ORDER BY avg_revenue_proxy DESC
""",
    "top_hosts": """
SELECT h.host_name, h.host_id, COUNT(*) AS properties
FROM core.fact_listings f
JOIN core.dim_host h ON f.host_key = h.host_key
GROUP BY 1,2 ORDER BY properties DESC LIMIT 20
""",
    "availability_by_district": """
SELECT ng.neighbourhood_group, MEDIAN(f.availability_365) AS median_availability_365
FROM core.fact_listings f
JOIN core.dim_neighbourhood_group ng ON f.ng_id = ng.ng_id
GROUP BY 1 ORDER BY median_availability_365
""",
    "reviews_monthly_by_ng": """
WITH rev AS (
  SELECT ng.neighbourhood_group,
         strftime(s.last_review, '%Y-%m') AS year_month,
         SUM(s.number_of_reviews) AS reviews
  FROM staging.airbnb_listings_clean s
  JOIN core.dim_neighbourhood_group ng
    ON COALESCE(s.neighbourhood_group,'UNKNOWN') = ng.neighbourhood_group
  WHERE s.last_review IS NOT NULL
  GROUP BY 1,2
)
SELECT * FROM rev ORDER BY neighbourhood_group, year_month
"""
}

def _strip_sql(sql: str) -> str:
    # quita espacios y ; finales que rompen COPY ( ... )
    return sql.strip().rstrip(";").strip()

def main():
    con = duckdb.connect(str(DUCKDB_PATH))
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    for name, sql in QUERIES.items():
        sql_clean = _strip_sql(sql)
        out = (GOLD_DIR / f"{name}.csv").as_posix()
        # En DuckDB 1.0 sirve WITH(HEADER, DELIMITER ',')
        con.execute(f"COPY ({sql_clean}) TO '{out}' WITH (HEADER, DELIMITER ',');")
    con.close()
    logging.info("GOLD: CSVs generados en data/gold")
    print("OK GOLD → CSVs en data/gold")

if __name__ == "__main__":
    main()
