
from datetime import datetime, timedelta

from airflow.sdk import DAG, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.microsoft.azure.operators.data_factory import (
    AzureDataFactoryRunPipelineOperator
)


default_args = {
    "owner": "capstone",
    "depends_on_past": False,
    "start_date": datetime(2026, 11, 5),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@task()
def extract_data_from_api():
    from include.upload_raw_data import upload_data

    api_response = upload_data()
    return api_response


@task()
def transform_data():
    from include.transform import transform

    cleaned_data = transform()
    return cleaned_data


with DAG(
    dag_id="urban_city_requests",
    catchup=False,
    default_args=default_args,
    schedule=None,
    max_active_runs=1,
) as dag:

    create_db_table = SQLExecuteQueryOperator(
        task_id="urban_city_table",
        sql="sql/urban_city.sql",
        conn_id="postgres_conn",
    )

    data_factory_pipeline = AzureDataFactoryRunPipelineOperator(
        task_id="run_data_factory",

        # Original pipeline - temporarily disabled
        # pipeline_name="UrbanCityDataFactoryPipeline",

        # Staging pipeline for assignment testing
        pipeline_name="UrbanCityDataFactoryPipeline_StagingTest",

        azure_data_factory_conn_id="azure_factory",
        factory_name="urban-cities-factory1",
        resource_group_name="service_requests",
        wait_for_termination=True,
        check_interval=30,
        retries=0,
    )

    bronze_task = extract_data_from_api()
    silver_task = transform_data()

    (
        bronze_task
        >> silver_task
        >> create_db_table
        >> data_factory_pipeline
    )

