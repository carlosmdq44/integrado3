-- sql/core_third.sql
CREATE SCHEMA IF NOT EXISTS core;

-- 1) Bucketización de disponibilidad (útil para cortes)
CREATE OR REPLACE TABLE core.dim_availability_bucket AS
SELECT
  bucket_id,
  bucket_label,
  min_days,
  max_days
FROM (
  SELECT 1 AS bucket_id, '0-60'::TEXT    AS bucket_label, 0   AS min_days, 60  AS max_days UNION ALL
  SELECT 2,              '61-180',                      61,  180           UNION ALL
  SELECT 3,              '181-300',                    181,  300           UNION ALL
  SELECT 4,              '301-365',                    301,  365
);

-- 2) Features de texto (integración no estructurado -> estructurado)
--    partimos de staging.listing_text_features (creado en normalize_external.py)
CREATE OR REPLACE TABLE core.listing_text_features AS
SELECT
  f.listing_id,
  tf.has_wifi,
  tf.has_pool,
  tf.has_garden,
  tf.is_luxury,
  tf.near_subway
FROM core.fact_listings f
LEFT JOIN staging.listing_text_features tf
  ON f.listing_id = tf.id;

-- 3) Enriquecer fact con bucket de disponibilidad
CREATE OR REPLACE TABLE core.fact_listings_enriched AS
SELECT
  f.*,
  ab.bucket_id,
  ab.bucket_label
FROM core.fact_listings f
LEFT JOIN core.dim_availability_bucket ab
  ON f.availability_365 BETWEEN ab.min_days AND ab.max_days;
