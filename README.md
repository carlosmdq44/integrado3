# Proyecto Integrador — Avances 1, 2, 3 y 4

## 🎯 Objetivo General
Diseñar e implementar un **pipeline ELT** escalable que integre datos de múltiples fuentes, los cargue en un **Data Warehouse**, y lo orqueste con **Airflow**, asegurando calidad continua mediante **CI/CD en GitHub Actions**.  

El proyecto se desarrolla en **cuatro entregas principales**:

1. **Avance 1:** Pipeline ELT base con CSV Airbnb NYC → DWH local (DuckDB).  
2. **Avance 2:** Recolección desde **APIs y Scraping**, contenerización con Docker, validación en capa raw.  
3. **Avance 3:** Transformaciones avanzadas en **SQL/Python**, integración de datos no estructurados, validación de capas staging/core/gold.  
4. **Avance 4:** **Orquestación con Apache Airflow** y **CI/CD con GitHub Actions** para ejecución automática y publicación de imágenes Docker.

---

## 🏗️ Diagrama General (ASCII – Fallback)

FUENTES

├─ CSV: AB_NYC.csv

├─ APIs

└─ Scraping

│

▼
EXTRACCIÓN (Python)

├─ extract_api.py

├─ extract_scrape.py

└─ run_extract.py (config YAML)

│

▼

RAW (data/raw)

├─ ab_nyc_YYYYMMDD.csv

├─ external/.json + manifest.csv

└─ validate_raw.py → docs/raw_validation_report.md

│
▼

STAGING (DuckDB)

├─ airbnb_listings_clean

├─ listing_text_features

└─ external (JSON normalizado)

│

▼

CORE (DuckDB)

├─ fact_listings

├─ dim_availability_bucket

└─ fact_listings_enriched

│

▼

GOLD (DuckDB + CSV)

├─ avg_price_by_area.csv

├─ room_type_offer.csv

├─ availability_bucket_by_ng.csv

├─ corr_availability_reviews_by_ng.csv

└─ price_vs_text_features.csv

│

▼

CONSUMO

├─ notebooks/analisis_airbnb.ipynb

└─ Dashboards BI

ORQUESTACIÓN / DEVOPS

├─ Airflow (DAGs: pipeline_airbnb_runall.py)

├─ Dockerfile + docker-compose.yml

├─ GitHub Actions (CI/CD + GHCR)

└─ quality_checks.py / validate_transform.py


---

## 🚀 Avance 1 — Pipeline ELT + Data Warehouse

**Fuente principal:**  
- CSV: `AB_NYC.csv` (Airbnb NYC dataset)

**Pipeline:**  
1. **Extract:** CSV → `data/raw/airbnb/ab_nyc_YYYYMMDD.csv`  
2. **Load:** `raw.airbnb_listings` (DuckDB)  
3. **Transform:** staging (limpieza/tipos/winsor), core (modelo dimensional), gold (KPIs)  

**Capas DWH (DuckDB):**
- `raw` → crudo  
- `staging` → limpio, tipificado  
- `core` → hechos + dimensiones  
- `gold` → datasets finales listos para BI  

**Resultados (gold):**
- `avg_price_by_area.csv`  
- `room_type_offer.csv`  
- `room_type_revenue_proxy.csv`  
- `top_hosts.csv`  
- `availability_by_district.csv`  
- `reviews_monthly_by_ng.csv`  

👉 Notebook: [`notebooks/analisis_airbnb.ipynb`](notebooks/analisis_airbnb.ipynb) con respuestas a Q1–Q8.

---

## 🌐 Avance 2 — Extracción desde APIs y Scraping + Docker

**Scripts principales:**
- `extract_api.py` → llamadas a APIs (requests + retries).  
- `extract_scrape.py` → scraping con BeautifulSoup.  
- `run_extract.py` → lee `config/extract_config.yaml` y ejecuta jobs.  
- `validate_raw.py` → genera reporte en `docs/raw_validation_report.md`.

**Docker:**
- Imagen base: `python:3.11-slim`  
- Instala `requirements.txt`  
- Copia `scripts/` y `config/`  
- `ENTRYPOINT` → `run_extract.py`  

**Convenciones capa RAW:**
- Archivos nombrados como `fuente_TIMESTAMP.json`  
- Manifest global: `data/raw/_manifest.csv`  

---

## 🔄 Avance 3 — Transformaciones Avanzadas

**Objetivo:**  
- Enriquecer **core** con datos derivados de texto + JSON externos.  
- Crear nuevas métricas en **gold**.

**Scripts clave:**
- `normalize_external.py` → features de texto (`has_wifi`, `is_luxury`, etc.).  
- `sql_runner.py` → ejecuta SQL desde `/sql`.  
- `sql/core_third.sql` → tablas enriquecidas en `core`.  
- `sql/gold_third.sql` → nuevos outputs `gold`.  
- `validate_transform.py` → asegura consistencia.  

**Análisis extra:**
- Impacto de amenities (wifi, piscina, etc.) en precio.  
- Correlación entre disponibilidad y reseñas.  
- Buckets de disponibilidad (0–60, 61–180, etc.).

---

## ⚙️ Avance 4 — Orquestación con Airflow + CI/CD

**Airflow (docker-compose en `/airflow`):**
- Servicios: `airflow-postgres`, `airflow-scheduler`, `airflow-webserver`.  
- Usuario admin creado automáticamente (`admin/admin`).  
- DAG principal: `pipeline_airbnb_runall.py`  
  - Orquesta extract, load, transform, gold, quality.  
  - Schedule: `@daily`.  

**CI/CD (GitHub Actions):**
- Workflows en `.github/workflows/`:
  - `ci.yml` → lint + parse DAGs.  
  - `pipeline-smoke.yml` → test end-to-end con CSV pequeño.  
  - `docker-publish.yml` → build & push imagen a **GHCR**.  
- Imagen disponible en:  
docker pull ghcr.io/carlosmdq44/integrador3-elt:latest

---

## 📂 Estructura del Proyecto

elt_airbnb_nyc/
├─ data/
│ ├─ raw/ # CSV/JSON originales
│ ├─ staging/ # datos limpios
│ ├─ core/ # modelo dimensional
│ ├─ gold/ # datasets listos para BI
│ └─ warehouse.duckdb
├─ scripts/
│ ├─ extract_*.py
│ ├─ normalize_external.py
│ ├─ sql_runner.py
│ ├─ quality_checks.py
│ └─ validate_transform.py
├─ sql/
│ ├─ core_third.sql
│ └─ gold_third.sql
├─ config/
│ └─ extract_config.yaml
├─ airflow/
│ ├─ docker-compose.yml
│ └─ dags/pipeline_airbnb_runall.py
├─ notebooks/
│ └─ analisis_airbnb.ipynb
├─ docs/
│ └─ raw_validation_report.md
├─ Dockerfile
├─ docker-compose.yml
├─ run.py
└─ .github/workflows/
├─ ci.yml
├─ pipeline-smoke.yml
└─ docker-publish.yml

---

## ✅ Estado de Entregas

- **Avance 1**  
  ✔ Pipeline ELT end-to-end (CSV → raw → staging → core → gold)  
  ✔ Respuestas Q1–Q8  

- **Avance 2**  
  ✔ Extracción desde APIs/scraping  
  ✔ Validación en capa raw  
  ✔ Dockerfile y ejecución contenerizada  

- **Avance 3**  
  ✔ Transformaciones SQL/Python avanzadas  
  ✔ Integración datos no estructurados  
  ✔ Nuevas métricas gold  

- **Avance 4**  
  ✔ Orquestación con Airflow  
  ✔ CI/CD con GitHub Actions  
  ✔ Publicación automática en GHCR  
