-- sql/gold_third.sql
CREATE SCHEMA IF NOT EXISTS gold;

-- Q1/Q2 refinado: precio medio por barrio/distrito y tipo habitación
CREATE OR REPLACE TABLE gold.avg_price_by_area_room AS
SELECT
  ng.neighbourhood_group,
  n.neighbourhood,
  r.room_type,
  AVG(f.price_winsor) AS avg_price
FROM core.fact_listings f
JOIN core.dim_neighbourhood n ON f.n_id = n.n_id
JOIN core.dim_neighbourhood_group ng ON f.ng_id = ng.ng_id
JOIN core.dim_room_type r ON f.rt_id = r.rt_id
GROUP BY 1,2,3;

-- Q4: mediana disponibilidad por bucket + distrito
CREATE OR REPLACE TABLE gold.availability_bucket_by_ng AS
SELECT
  ng.neighbourhood_group,
  fe.bucket_label,
  MEDIAN(fe.availability_365) AS median_availability
FROM core.fact_listings_enriched fe
JOIN core.dim_neighbourhood_group ng ON fe.ng_id = ng.ng_id
GROUP BY 1,2
ORDER BY 1,2;

-- Q8: correlación disponibilidad vs reseñas por distrito
CREATE OR REPLACE TABLE gold.corr_availability_reviews_by_ng AS
SELECT
  ng.neighbourhood_group,
  corr(fe.availability_365, fe.number_of_reviews) AS corr_avail_reviews
FROM core.fact_listings_enriched fe
JOIN core.dim_neighbourhood_group ng ON fe.ng_id = ng.ng_id
GROUP BY 1
ORDER BY 1;

-- Extra: impacto de features de texto en precio
CREATE OR REPLACE TABLE gold.price_vs_text_features AS
SELECT
  r.room_type,
  ltf.has_wifi,
  ltf.has_pool,
  ltf.is_luxury,
  AVG(f.price_winsor) AS avg_price
FROM core.fact_listings f
JOIN core.listing_text_features ltf ON f.listing_id = ltf.listing_id
JOIN core.dim_room_type r ON f.rt_id = r.rt_id
GROUP BY 1,2,3,4
ORDER BY 1,2,3,4;
