# Proyecto Integrador — Avances 1, 2 y 3

## 🎯 Objetivo General
Diseñar e implementar un **pipeline ELT** escalable que integre datos de múltiples fuentes, los cargue en un **Data Warehouse** y los transforme en datasets listos para análisis de negocio.  

El proyecto se desarrolla en **tres entregas**:
1. **Avance 1:** Pipeline ELT base con CSV Airbnb NYC → DWH local (DuckDB).  
2. **Avance 2:** Recolección desde **APIs y Scraping**, contenerización con Docker, validación en capa raw.  
3. **Avance 3:** Transformaciones avanzadas en **SQL/Python**, integración de datos no estructurados, validación de capas staging/core/gold.  

---

## 🗺️ Diagrama General (Mermaid)
> GitHub renderiza Mermaid automáticamente. Si tu visor no lo soporta, abajo hay una versión ASCII.

```mermaid
flowchart LR
    %% ====== FUENTES ======
    subgraph FUENTES
      CSV[CSV: AB_NYC.csv]
      API[(APIs públicas/privadas)]
      SCR[Scraping Web]
    end

    %% ====== EXTRACCIÓN ======
    subgraph EXTRACCIÓN (Python)
      EX_API[extract_api.py\n+ requests + retries]
      EX_SCR[extract_scrape.py\n+ BeautifulSoup]
      RUN_YAML[run_extract.py\n(config/extract_config.yaml)]
    end

    %% ====== RAW ======
    subgraph RAW (data/raw)
      RAW_CSV[airbnb/ab_nyc_YYYYMMDD.csv]
      RAW_EXT[external/*.json\n+ _manifest.csv]
      VALID_RAW[validate_raw.py\n→ docs/raw_validation_report.md]
    end

    %% ====== STAGING ======
    subgraph STAGING (DuckDB)
      STG_CLEAN[staging.airbnb_listings_clean\n(cleaning, types, winsor)]
      STG_TEXT[staging.listing_text_features\n(text -> features)]
      STG_EXT[staging.external_* (JSON normalizado)]
    end

    %% ====== CORE ======
    subgraph CORE (DuckDB)
      FACT[fact_listings]
      LTF[core.listing_text_features]
      AVB[core.dim_availability_bucket]
      FACT_ENR[core.fact_listings_enriched]
    end

    %% ====== GOLD ======
    subgraph GOLD (DuckDB + CSV)
      G1[gold.avg_price_by_area.csv]
      G2[gold.room_type_offer.csv]
      G3[gold.room_type_revenue_proxy.csv]
      G4[gold.top_hosts.csv]
      G5[gold.availability_by_district.csv]
      G6[gold.reviews_monthly_by_ng.csv]
      G7[gold.avg_price_by_area_room]
      G8[gold.availability_bucket_by_ng]
      G9[gold.corr_availability_reviews_by_ng]
      G10[gold.price_vs_text_features]
    end

    %% ====== CONSUMO ======
    subgraph CONSUMO
      NB[notebooks/analisis_airbnb.ipynb]
      BI[Dashboards/BI\n(Tableau/PowerBI/QuickSight)]
    end

    %% ====== ORQUESTACIÓN / DEVOPS ======
    subgraph ORQ_DEVOPS
      RUN[run.py (A1)]
      SQLRUN[sql_runner.py (A3)]
      NORM[normalize_external.py (A3)]
      QCHK[quality_checks.py]
      VAL_T[validate_transform.py (A3)]
      DK[(Dockerfile\nExtractor A2)]
      CI[GitHub Actions\nbuild/push image]
      AFX[(Airflow - futuro)]
    end

    %% FLUJOS
    CSV --> RAW_CSV
    API --> EX_API --> RUN_YAML --> RAW_EXT
    SCR --> EX_SCR --> RUN_YAML --> RAW_EXT
    RAW_EXT --> VALID_RAW
    RAW_CSV --> STG_CLEAN
    RAW_EXT --> STG_EXT
    STG_CLEAN --> FACT
    STG_CLEAN --> NORM --> STG_TEXT
    STG_TEXT --> LTF
    FACT --> FACT_ENR
    AVB --> FACT_ENR

    FACT_ENR --> G7 & G8 & G9 & G10
    FACT --> G1 & G2 & G3 & G4 & G5 & G6

    G1 & G2 & G3 & G4 & G5 & G6 & G7 & G8 & G9 & G10 --> NB
    G1 & G7 & G8 & G9 & G10 --> BI

    RUN --> STG_CLEAN
    SQLRUN --> CORE & GOLD
    QCHK --> CORE
    VAL_T --> GOLD
    DK --> RUN_YAML
    CI --> DK
    AFX -. futuro .- RUN_YAML
    AFX -. futuro .- SQLRUN
```

### Diagrama (ASCII – Fallback)
```
FUENTES
  ├─ CSV: AB_NYC.csv
  ├─ APIs
  └─ Scraping
        │
        ▼
EXTRACCIÓN (Python)
  ├─ extract_api.py (requests + retries)
  ├─ extract_scrape.py (BeautifulSoup)
  └─ run_extract.py (config YAML)
        │
        ▼
RAW (data/raw)
  ├─ airbnb/ab_nyc_YYYYMMDD.csv
  ├─ external/*.json + _manifest.csv
  └─ validate_raw.py → docs/raw_validation_report.md
        │
        ▼
STAGING (DuckDB)
  ├─ staging.airbnb_listings_clean (cleaning, types, winsor)
  ├─ staging.listing_text_features (texto→features)
  └─ staging.external_* (JSON normalizado)
        │
        ▼
CORE (DuckDB)
  ├─ fact_listings
  ├─ core.listing_text_features
  ├─ core.dim_availability_bucket
  └─ core.fact_listings_enriched
        │
        ▼
GOLD (DuckDB + CSV)
  ├─ avg_price_by_area.csv, room_type_offer.csv, ...
  ├─ avg_price_by_area_room
  ├─ availability_bucket_by_ng
  ├─ corr_availability_reviews_by_ng
  └─ price_vs_text_features
        │
        ▼
CONSUMO
  ├─ notebooks/analisis_airbnb.ipynb
  └─ Dashboards/BI (Tableau/PowerBI/QuickSight)

ORQUESTACIÓN / DEVOPS
  ├─ run.py (Avance 1)
  ├─ sql_runner.py / normalize_external.py (Avance 3)
  ├─ quality_checks.py / validate_transform.py
  ├─ Dockerfile (Extractor Avance 2)
  ├─ GitHub Actions (build/push image)
  └─ Airflow (futuro)
```

---

## 🏗️ Avance 1 — Pipeline ELT + Data Warehouse

**Fuente principal:**  
- CSV: `AB_NYC.csv` (Airbnb NYC dataset)

**Pipeline:**  
1) **Extract:** CSV → `data/raw/airbnb/ab_nyc_YYYYMMDD.csv`  
2) **Load:** `raw.airbnb_listings` (DuckDB)  
3) **Transform:** staging (limpieza/tipos/winsor), core (modelo dimensional), gold (KPIs)  

**Capas DWH (DuckDB):**  
- `raw` → crudo  
- `staging` → limpio, tipificado, `price_winsor`  
- `core` → hechos + dimensiones  
- `gold` → datasets finales

**Resultados (gold):**  
- `avg_price_by_area.csv`  
- `room_type_offer.csv`  
- `room_type_revenue_proxy.csv`  
- `top_hosts.csv`  
- `availability_by_district.csv`  
- `reviews_monthly_by_ng.csv`  

**Notebook:** [`notebooks/analisis_airbnb.ipynb`](notebooks/analisis_airbnb.ipynb) con Q1–Q8.

---

## 🌐 Avance 2 — Extracción desde APIs y Scraping + Docker

**Scripts:**  
- `extract_api.py` (APIs, reintentos/timeout)  
- `extract_scrape.py` (BeautifulSoup, meta + links)  
- `run_extract.py` (lee `config/extract_config.yaml`)  
- `validate_raw.py` (reporte: `docs/raw_validation_report.md`)  

**Convenciones RAW:**  
- Nombres: `fuente_YYYYMMDDThhmmssZ.json` (UTF-8, `\n`)  
- Manifest: `data/raw/_manifest.csv` (source, type, path, bytes, sha256)

**Docker (extractor):**  
- Imagen base: `python:3.10-slim`  
- Instala `requirements.txt`  
- Copia `scripts/` y `config/`  
- `ENTRYPOINT` → `run_extract.py`  

**Ejemplo de jobs (`config/extract_config.yaml`):**
```yaml
jobs:
  - type: api
    name: httpbin_get_ip
    endpoint: https://httpbin.org/ip
  - type: scrape
    name: python_org_home
    url: https://www.python.org/
```

---

## 🔄 Avance 3 — Transformaciones avanzadas + integración no estructurado

**Objetivo:** integrar **no estructurado → estructurado** y enriquecer **core** para nuevos **gold**.  

**Scripts clave:**  
- `normalize_external.py`  
  - Texto libre de `name` (listings) → features: `has_wifi`, `has_pool`, `has_garden`, `is_luxury`, `near_subway`.  
  - Normaliza JSON externos a `staging.external_*`.  
- `sql_runner.py` (ejecuta SQL)  
- `sql/core_third.sql`  
  - `core.listing_text_features`  
  - `core.dim_availability_bucket`  
  - `core.fact_listings_enriched`  
- `sql/gold_third.sql`  
  - `gold.avg_price_by_area_room`  
  - `gold.availability_bucket_by_ng`  
  - `gold.corr_availability_reviews_by_ng`  
  - `gold.price_vs_text_features`  
- `validate_transform.py` (checks de existencia/coherencia)  

**Ejemplos de análisis nuevos:**  
- Impacto de `has_wifi` / `is_luxury` en precio.  
- Correlación entre `availability_365` y `number_of_reviews` por distrito.  
- Buckets de disponibilidad (`0–60`, `61–180`, `181–300`, `301–365`).  

---

## 📂 Estructura consolidada del proyecto

```
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
```

---

## ✅ Estado de entregas

- **Avance 1**  
  - [x] Pipeline ELT (CSV → raw → staging → core → gold)  
  - [x] Respuestas Q1–Q8 en notebook  

- **Avance 2**  
  - [x] Extracción APIs + Scraping (YAML configurable)  
  - [x] Validación capa raw + reporte  
  - [x] Contenerización con Docker  

- **Avance 3**  
  - [x] Transformaciones avanzadas SQL/Python  
  - [x] Integración datos no estructurados (texto + JSON externos)  
  - [x] Validación de staging/core/gold  
