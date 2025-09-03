# airflow/dags/pipeline_airbnb_steps.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

# Dentro de los contenedores de Airflow, tu repo está montado en:
BASE_DIR = "/opt/airflow/project"

# Permitimos parametrizar el CSV desde Variables de Airflow (UI > Admin > Variables)
CSV_PATH = Variable.get(
    "airbnb_csv_path",
    default_var=f"{BASE_DIR}/data/raw/airbnb/AB_NYC.csv"
)

default_args = {
    "owner": "carlos",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="elt_airbnb_steps",
    description="ELT Airbnb NYC dividido en tareas (extract→load→staging→core→gold→quality)",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",   # poné None si preferís correr manual
    catchup=False,
    tags=["elt", "airbnb", "duckdb", "steps"],
) as dag:

    # Pre-chequeo: que exista el CSV
    check_csv = BashOperator(
        task_id="check_csv_exists",
        bash_command=f'if [ ! -f "{CSV_PATH}" ]; then echo "CSV no encontrado: {CSV_PATH}" && exit 1; fi'
    )

    extract = BashOperator(
        task_id="extract",
        bash_command=f"python {BASE_DIR}/scripts/extract.py {CSV_PATH}",
    )

    load = BashOperator(
        task_id="load",
        bash_command=f"python {BASE_DIR}/scripts/load.py",
    )

    staging = BashOperator(
        task_id="transform_staging",
        bash_command=f"python {BASE_DIR}/scripts/transform_staging.py",
    )

    core = BashOperator(
        task_id="transform_core",
        bash_command=f"python {BASE_DIR}/scripts/transform_core.py",
    )

    gold = BashOperator(
        task_id="gold",
        bash_command=f"python {BASE_DIR}/scripts/gold.py",
    )

    quality = BashOperator(
        task_id="quality_checks",
        bash_command=f"python {BASE_DIR}/scripts/quality_checks.py",
    )

    # Dependencias
    check_csv >> extract >> load >> staging >> core >> gold >> quality
