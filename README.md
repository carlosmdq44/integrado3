# Proyecto Integrador — Primer Avance
## Pipeline ELT + Data Warehouse (Airbnb NYC)

### 🎯 Objetivo del pipeline
Diseñar e implementar un **pipeline ELT** que integre datos de múltiples fuentes, los cargue en un Data Warehouse escalable y los transforme en datasets listos para análisis y visualización, respondiendo preguntas clave del negocio.

---

## 🏗️ Arquitectura general

**Fuentes de datos:**
- CSV: `AB_NYC.csv` (Airbnb NYC dataset)
- Futuro: APIs, bases internas, sensores

**Pipeline ELT:**

1. **Extract (E)** → copiamos el CSV original en la carpeta `data/raw/airbnb/` con fecha (ej. `ab_nyc_20250831.csv`).  
2. **Load (L)** → cargamos los datos sin transformar en DuckDB (`raw.airbnb_listings`).  
3. **Transform (T)** → realizamos transformaciones en Python + DuckDB:
   - Limpieza (staging)
   - Modelado dimensional (core)
   - Agregados y KPIs listos para negocio (gold)

**Data Warehouse (DuckDB, local):**
- `raw` → datos crudos
- `staging` → datos limpios, tipificados, sin duplicados, con `price_winsor` (outliers controlados)
- `core` → modelo de negocio (hechos y dimensiones)
- `gold` → datasets listos para análisis y BI

**Orquestación:**  
- Por ahora, un script `run.py` que ejecuta todo el pipeline paso a paso.  
- Futuro: Apache Airflow para DAGs.

**CI/CD:**  
- Por ahora, `quality_checks.py` asegura unicidad de IDs, precios válidos y tablas core no vacías.  
- Futuro: GitHub Actions para automatizar tests y despliegues.

---

## 📂 Estructura del proyecto

```
elt_airbnb_nyc/
├─ data/
│  ├─ raw/airbnb/      # CSVs originales con fecha
│  ├─ staging/         # CSVs limpios
│  ├─ core/            # tablas de negocio (DuckDB)
│  └─ gold/            # datasets agregados para análisis
├─ scripts/            # extract, load, transform, gold, quality
├─ notebooks/          # análisis exploratorio (analisis_airbnb.ipynb)
├─ docs/               # documentación + gráficos generados
├─ logs/               # logs de ejecución
├─ run.py              # orquestador del pipeline
└─ .env                # configuración de rutas
```

---

## 🚀 Ejecución del pipeline

1. Crear entorno virtual e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Ejecutar el pipeline pasando la ruta al CSV original:

```bash
python run.py "data/raw/airbnb/AB_NYC.csv"
```

3. Resultados:
- Warehouse DuckDB en `data/warehouse.duckdb`
- Staging CSV en `data/staging/airbnb_listings_clean.csv`
- Tablas core en DuckDB (`core.*`)
- Archivos gold en `data/gold/`:
  - `avg_price_by_area.csv`
  - `room_type_offer.csv`
  - `room_type_revenue_proxy.csv`
  - `top_hosts.csv`
  - `availability_by_district.csv`
  - `reviews_monthly_by_ng.csv`

---

## 📊 Preguntas de negocio abordadas (Q1–Q8)

1. Precio promedio por barrio y distrito → `avg_price_by_area.csv`
2. Tipo de habitación más ofrecido y revenue estimado → `room_type_offer.csv` + `room_type_revenue_proxy.csv`
3. Anfitriones con más propiedades y variación de precios → `top_hosts.csv` + análisis en staging
4. Disponibilidad anual por barrio/tipo → `availability_by_district.csv` + query extra
5. Evolución de reseñas mensuales por distrito → `reviews_monthly_by_ng.csv`
6. Barrios con mayor concentración de alojamientos activos → query en staging
7. Distribución de precios y outliers → comparación `price` vs `price_winsor`
8. Relación entre disponibilidad y reseñas → scatter + correlación

Todos los análisis están documentados en el notebook:  
👉 [`notebooks/analisis_airbnb.ipynb`](../notebooks/analisis_airbnb.ipynb)

---

## 🛠️ Justificación de herramientas

- **Python + Pandas**: limpieza y exploración inicial.  
- **DuckDB**: data warehouse ligero, SQL estándar, soporta tablas por esquema (`raw`, `staging`, `core`, `gold`).  
- **Matplotlib**: visualización de KPIs.  
- **dotenv + logging**: buenas prácticas de configuración y trazabilidad.  
- **Jupyter Notebook**: análisis incremental y presentación.  
- **Airflow/DBT (futuro)**: escalar orquestación y versionado de transformaciones.  
- **GitHub Actions (futuro)**: CI/CD automatizado.

---

## ✅ Estado del Primer Avance

- [x] Pipeline ELT funcionando end-to-end  
- [x] Capas de DWH definidas (raw, staging, core, gold)  
- [x] Tablas gold que responden Q1–Q8  
- [x] Notebook con análisis y gráficos  
- [x] Documentación técnica (este README)  
- [ ] Orquestación Airflow (pendiente próximo avance)  
- [ ] CI/CD con GitHub Actions (pendiente próximo avance)  

---

## 📌 Entregables
- `docs/README_PrimerAvance.md` (este documento)  
- `notebooks/analisis_airbnb.ipynb` (respuestas Q1–Q8 con gráficos)  
- `data/gold/*.csv` (datasets listos para BI)  
- Capturas de ejecución del pipeline y gráficos en `docs/`
