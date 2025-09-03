from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Tu repo se monta en /opt/airflow/project dentro de los contenedores de Airflow
BASE_DIR = "/opt/airflow/project"
CSV_PATH = f"{BASE_DIR}/data/raw/airbnb/AB_NYC.csv"  # <-- cambiá si tu CSV se llama distinto

default_args = {
    "owner": "carlos",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="elt_airbnb_runall",
    description="Ejecuta run.py (pipeline completo) con Airflow",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",   # o None si querés lanzar manual
    catchup=False,
    tags=["elt", "airbnb", "duckdb"],
) as dag:

    check_csv = BashOperator(
        task_id="check_csv_exists",
        bash_command=f'if [ ! -f "{CSV_PATH}" ]; then echo "CSV no encontrado: {CSV_PATH}" && exit 1; fi'
    )

    run_all = BashOperator(
        task_id="run_all",
        bash_command=f"python {BASE_DIR}/run.py {CSV_PATH}",
    )

    check_csv >> run_all
