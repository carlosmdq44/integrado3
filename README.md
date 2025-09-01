Proyecto Integrador — Avances 1, 2 y 3
🎯 Objetivo General

Diseñar e implementar un pipeline ELT escalable que integre datos de múltiples fuentes, los cargue en un Data Warehouse y los transforme en datasets listos para análisis de negocio.

El proyecto se desarrolla en tres entregas:

Avance 1: Pipeline ELT base con CSV Airbnb NYC → DWH local (DuckDB).

Avance 2: Recolección desde APIs y Scraping, contenerización con Docker, validación en capa raw.

Avance 3: Transformaciones avanzadas en SQL/Python, integración de datos no estructurados, validación de capas staging/core/gold.

🏗️ Avance 1 — Pipeline ELT + Data Warehouse

Fuentes:

CSV: AB_NYC.csv (Airbnb NYC dataset)

Pipeline:

Extract: copia de CSV a data/raw/airbnb/ con fecha.

Load: carga en raw.airbnb_listings (DuckDB).

Transform: limpieza en staging, modelo dimensional en core, KPIs en gold.

Data Warehouse (DuckDB):

raw → crudo

staging → limpio, tipificado

core → hechos + dimensiones

gold → datasets finales

Resultados principales:

gold.avg_price_by_area.csv

gold.room_type_offer.csv

gold.room_type_revenue_proxy.csv

gold.top_hosts.csv

gold.availability_by_district.csv

gold.reviews_monthly_by_ng.csv

Preguntas Q1–Q8 resueltas en notebooks/analisis_airbnb.ipynb
.

🌐 Avance 2 — Extracción desde APIs y Scraping + Docker

Novedades:

Scripts Python parametrizados por YAML:

extract_api.py (APIs con requests + reintentos).

extract_scrape.py (web scraping con BeautifulSoup).

run_extract.py (ejecuta jobs definidos en config/extract_config.yaml).

Validación de archivos raw (validate_raw.py) → genera docs/raw_validation_report.md.

Convención de nombres: fuente_fecha.json.

Manifest automático _manifest.csv.

Dockerfile:

Imagen base: python:3.10-slim

Instala requirements.txt

Copia scripts y config

ENTRYPOINT → run_extract.py

Ejemplo de jobs:

jobs:
  - type: api
    name: httpbin_get_ip
    endpoint: https://httpbin.org/ip
  - type: scrape
    name: python_org_home
    url: https://www.python.org/


Resultados:

Archivos .json en data/raw/external/.

Validación OK → reporte con tamaño, formato y estado.

Imagen Docker lista para docker build y docker run.

🔄 Avance 3 — Transformaciones avanzadas + integración no estructurado

Objetivo: convertir datos crudos en información útil para negocio, integrando fuentes estructuradas y no estructuradas.

Scripts principales:

normalize_external.py →

Convierte texto libre (name de listings) en features tabulares (has_wifi, has_pool, etc.).

Normaliza JSON externos (httpbin, scraping) en tablas staging.

sql_runner.py → ejecuta transformaciones SQL.

sql/core_third.sql → crea:

core.listing_text_features

core.fact_listings_enriched (con buckets de disponibilidad).

sql/gold_third.sql → genera datasets de consumo:

gold.avg_price_by_area_room

gold.availability_bucket_by_ng

gold.corr_availability_reviews_by_ng

gold.price_vs_text_features

validate_transform.py → checks automáticos de existencia y consistencia.

Ejemplo de nuevas métricas:

Impacto de has_wifi o is_luxury en el precio promedio.

Correlación entre disponibilidad y cantidad de reseñas por distrito.

Distribución de disponibilidad anual por buckets (0–60, 61–180, etc.).

Resultados:

Validación final: OK VALIDATE TRANSFORM ✔

Nuevas tablas core + gold disponibles en data/warehouse.duckdb.

📂 Estructura consolidada del proyecto
elt_airbnb_nyc/
├─ data/
│  ├─ raw/               # CSV/JSON originales
│  ├─ staging/           # CSV limpios / features tabulares
│  ├─ core/              # modelo de negocio
│  ├─ gold/              # datasets finales
│  └─ warehouse.duckdb   # DWH local
├─ scripts/
│  ├─ extract_*.py       # extracción (APIs, scraping)
│  ├─ normalize_external.py
│  ├─ sql_runner.py
│  ├─ validate_transform.py
│  └─ quality_checks.py
├─ sql/                  # transformaciones SQL (core, gold)
├─ config/               # extract_config.yaml
├─ notebooks/            # analisis_airbnb.ipynb
├─ docs/                 # documentación + reportes
├─ Dockerfile            # extractor (avance 2)
└─ run.py                # pipeline avance 1

✅ Estado de entregas

Avance 1

 Pipeline ELT (CSV → raw → staging → core → gold)

 Respuestas Q1–Q8 en notebook

Avance 2

 Extracción APIs + Scraping (YAML configurable)

 Validación capa raw + reporte

 Contenerización con Docker

Avance 3

 Transformaciones avanzadas SQL/Python

 Integración datos no estructurados (texto + JSON externos)

 Validación de staging/core/gold
