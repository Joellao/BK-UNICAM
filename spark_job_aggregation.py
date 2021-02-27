from datetime import datetime, timedelta
from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2021, 2, 27),
    'email': ['joel.sina97@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}
dag = DAG(dag_id='spark_job_aggregation',
          default_args=default_args,
          catchup=False,
          schedule_interval="*/5 * * * *")


spark_conf = {
    'spark.mongodb.output.uri':'mongodb+srv://ubuntu:123stella@cluster0.aajvl.mongodb.net/ResultsDA.sensors?retryWrites=true&w=majority'
}
nome = SparkSubmitOperator(
    task_id='aggregation',
    conn_id='spark_submit_standalone',
    application='/nfs/general/spark_jobs/SensorAggregationJob.py',
    application_args=["/nfs/general/files/2020_02_01T00_00_00_2020_03_01T00_00_00.csv","15"],
    packages='org.mongodb.spark:mongo-spark-connector_2.12:3.0.1',
    conf=spark_conf,
    name='sensor_aggr',
    dag=dag
    )
