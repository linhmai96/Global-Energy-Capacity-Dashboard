import os

from airflow import DAG
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from datetime import datetime

# 1. Read & validate env vars
required_env = {
    "GCP_PROJECT_ID"      : os.environ.get("GCP_PROJECT_ID"),
    "GCP_GCS_BUCKET"      : os.environ.get("GCP_GCS_BUCKET"),
    "DATAPROC_NAME"       : os.environ.get("DATAPROC_NAME"),
    "DATAPROC_TEMP_BUCKET": os.environ.get("DATAPROC_TEMP_BUCKET"),
    "BIGQUERY_DATASET"    : os.environ.get("BIGQUERY_DATASET"),
}
missing = [var_name for var_name, var_val in required_env.items() if not var_val]
if missing:
    raise ValueError(f"Missing required environment variable(s): {', '.join(missing)}")

PROJECT_ID   = required_env["GCP_PROJECT_ID"]
BUCKET       = required_env["GCP_GCS_BUCKET"]
CLUSTER_NAME = required_env["DATAPROC_NAME"]
TEMP_BUCKET  = required_env["DATAPROC_TEMP_BUCKET"]
DATASET      = required_env["BIGQUERY_DATASET"]

country_uri          = f"gs://{BUCKET}/data/country_code.csv"
powerplant_uri       = f"gs://{BUCKET}/data/global_power_plant_database.csv"
main_python_file_uri = f"gs://{BUCKET}/code/spark_data_transformation.py"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

# 2. Build the DAG
with DAG("transform_and_load",
        default_args=default_args,
        start_date = datetime(2025, 4, 6),
        end_date = datetime(2025, 4, 15),
        schedule_interval="@daily",
        catchup=True,
        max_active_runs=1,
        tags=["dtc"]
        ) as dag:

    # 1. Sensor to wait for DAG country_code_data
    wait_for_country_code_data = ExternalTaskSensor(
        task_id="wait_for_country_code_data",
        external_dag_id="country_code_data",
        external_task_id="final_cleanup",
        timeout=120,
        poke_interval=30,
        mode="poke"
    )

    # 2. Sensor to wait for DAG power_plant_data
    wait_for_power_plant_data = ExternalTaskSensor(
        task_id="wait_for_power_plant_data",
        external_dag_id="power_plant_data",
        external_task_id="final_cleanup",
        timeout=120,
        poke_interval=30,
        mode="poke"
    )

    # 3. Submit Spark job
    spark_job = {
        "reference": {"project_id": PROJECT_ID},
        "placement": {"cluster_name": CLUSTER_NAME},
        "pyspark_job": {
            "main_python_file_uri": f"{main_python_file_uri}",
            "args": [
                "--dataset", DATASET,
                "--temp-bucket", TEMP_BUCKET,
                "--country-uri", country_uri,
                "--powerplant-uri", powerplant_uri
            ]
        }
    }
    # 4. Run Dataproc
    transform_and_load = DataprocSubmitJobOperator(
        task_id="transform_and_load",
        job=spark_job,
        region="us-central1",
        project_id=PROJECT_ID
    )

    [wait_for_country_code_data, wait_for_power_plant_data] >> transform_and_load
