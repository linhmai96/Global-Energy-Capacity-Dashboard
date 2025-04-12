import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from google.cloud import storage

# 1. Read & validate env vars
required_env = {
    "GCP_GCS_BUCKET" : os.environ.get("GCP_GCS_BUCKET"),
    "COUNTRY_URL"    : os.environ.get("COUNTRY_URL"),
    "POWER_PLANT_URL": os.environ.get("POWER_PLANT_URL"),
}
missing = [var_name for var_name, var_val in required_env.items() if not var_val]
if missing:
    raise ValueError(f"Missing required environment variable(s): {', '.join(missing)}")

BUCKET          = required_env["GCP_GCS_BUCKET"]
COUNTRY_URL     = required_env["COUNTRY_URL"]
POWER_PLANT_URL = required_env["POWER_PLANT_URL"]

# 2. Build the DAG
def etl_dag(
    dag_id: str,
    schedule: str,
    start: datetime,
    end: datetime,
    url: str,
    download_path: str,
    gcs_path: str,
    unzip_path: str = None,
    extracted_file: str = None,
):
    """
    If unzip_path is None → simple download & upload.
    If unzip_path + extracted_file provided → download, unzip, upload.
    """
    default_args = {
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }

    dag = DAG(
        dag_id=dag_id,
        start_date=start,
        end_date=end,
        schedule_interval=schedule,
        default_args=default_args,
        catchup=True,
        max_active_runs=1,
        tags=["dtc"],
    )

    with dag:
        # 1. cleanup + download
        download = BashOperator(
            task_id="cleanup_and_download",
            bash_command=(
                f"rm -f {download_path}"
                + (f"&& rm -rf {unzip_path} " if unzip_path else "")
                + f"&& curl -sSLf {url} > {download_path}"
            ),
        )

        tasks = [download]

        # 2. optional unzip
        if unzip_path:
            unzip = BashOperator(
                task_id="unzip",
                bash_command=f"unzip {download_path} -d {unzip_path}",
            )
            tasks.append(unzip)
            upload_source = str(Path(unzip_path) / extracted_file)
        else:
            upload_source = download_path

        # 3. upload
        upload = LocalFilesystemToGCSOperator(
            task_id="upload_to_gcs",
            src=upload_source,
            dst=gcs_path,
            bucket=BUCKET,
        )
        tasks.append(upload)

        # 4. final cleanup
        cleanup = BashOperator(
            task_id="final_cleanup",
            bash_command=(
                f"rm -f {download_path}"
                + (f"&& rm -rf {unzip_path}*" if unzip_path else "")
            ),
        )
        tasks.append(cleanup)

        # 5. chain them all
        #    download >> [unzip?] >> upload >> cleanup
        for upstream, downstream in zip(tasks, tasks[1:]):
            upstream >> downstream

    return dag

# 3. Initiate both DAGs
country_code_dag = etl_dag(
    dag_id="country_code_data",
    schedule="@daily",
    start=datetime(2025, 4, 6),
    end=datetime(2025, 4, 15),
    url=COUNTRY_URL,
    download_path="/tmp/country_code.csv",
    gcs_path="data/country_code.csv",
)

power_plant_dag = etl_dag(
    dag_id="power_plant_data",
    schedule="@daily",
    start=datetime(2025, 4, 6),
    end=datetime(2025, 4, 15),
    url=POWER_PLANT_URL,
    download_path="/tmp/global_power_plant.zip",
    unzip_path="/tmp/extracted/",
    extracted_file="global_power_plant_database.csv",
    gcs_path="data/global_power_plant_database.csv",
)
