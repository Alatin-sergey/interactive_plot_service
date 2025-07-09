from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime
from airflow_utils import insert_300_objects_task

START_DATE = datetime.datetime(2025, 6, 23)


with DAG(
    dag_id="insert_300_objects",
    start_date=START_DATE,
    schedule_interval=None,
    catchup=False,
    tags=["insert", "interactive", "300 objects"]
) as dag:
    task = PythonOperator(
        task_id=f"insert_300_objects_task",
        python_callable=insert_300_objects_task,
    )
