import duckdb
from utils import DUCKDB_PATH, logging

SQL = r"""
CREATE SCHEMA IF NOT EXISTS core;

-- Dimensiones (IDs surrogate simples con DENSE_RANK)
CREATE OR REPLACE VIEW core.v_stg AS
SELECT * FROM staging.airbnb_listings_clean;

CREATE OR REPLACE TABLE core.dim_neighbourhood_group AS
SELECT DENSE_RANK() OVER (ORDER BY COALESCE(neighbourhood_group,'UNKNOWN')) AS ng_id,
       COALESCE(neighbourhood_group,'UNKNOWN') AS neighbourhood_group
FROM (SELECT DISTINCT neighbourhood_group FROM core.v_stg);

CREATE OR REPLACE TABLE core.dim_neighbourhood AS
SELECT DENSE_RANK() OVER (ORDER BY COALESCE(neighbourhood,'UNKNOWN')) AS n_id,
       COALESCE(neighbourhood,'UNKNOWN') AS neighbourhood
FROM (SELECT DISTINCT neighbourhood FROM core.v_stg);

CREATE OR REPLACE TABLE core.dim_room_type AS
SELECT DENSE_RANK() OVER (ORDER BY COALESCE(room_type,'UNKNOWN')) AS rt_id,
       COALESCE(room_type,'UNKNOWN') AS room_type
FROM (SELECT DISTINCT room_type FROM core.v_stg);

CREATE OR REPLACE TABLE core.dim_host AS
SELECT DENSE_RANK() OVER (ORDER BY COALESCE(host_id, -1)) AS host_key,
       host_id,
       host_name
FROM (SELECT DISTINCT host_id, host_name FROM core.v_stg);

-- Hechos (una fila por listing)
CREATE OR REPLACE TABLE core.fact_listings AS
SELECT
    s.id AS listing_id,
    h.host_key,
    rt.rt_id,
    n.n_id,
    ng.ng_id,
    s.price, s.price_winsor,
    s.minimum_nights,
    s.number_of_reviews,
    s.reviews_per_month,
    s.calculated_host_listings_count,
    s.availability_365,
    s.occupancy_proxy,
    s.revenue_proxy
FROM core.v_stg s
LEFT JOIN core.dim_host h ON s.host_id = h.host_id
LEFT JOIN core.dim_room_type rt ON COALESCE(s.room_type,'UNKNOWN') = rt.room_type
LEFT JOIN core.dim_neighbourhood n ON COALESCE(s.neighbourhood,'UNKNOWN') = n.neighbourhood
LEFT JOIN core.dim_neighbourhood_group ng ON COALESCE(s.neighbourhood_group,'UNKNOWN') = ng.neighbourhood_group;
"""

def main():
    con = duckdb.connect(str(DUCKDB_PATH))
    con.execute(SQL)
    con.close()
    logging.info("CORE: dims y fact generadas")
    print("OK CORE → dim_*, fact_listings")

if __name__ == "__main__":
    main()
