# BK#UNICAM 
## _An Apache Airflow & Apache Spark study_

The goal of this project is to calculate for each sensor of a data set, the aggregation of `minimum`, `maximum` and `average` in a timespan of `1 hour` with windows of `15 minutes`. Apache Airflow executes a scheduled Job written in Spark.
For this project multiple machines were taken in consideration in order to make an infrastracture with all connected. So we have a `cluster` of Spark oriented machines, a group of Airflow Machines and a machine that acts for Database purposes.

All the work has been executed in Linux `Ubuntu 20.04` machines:
- 3 Machines for Apache Spark
- 2 Machines for Apache Airflow
- 1 Machine for Database

We assume that Airflow will work with spark-submit-operator so spark-submit binaries should be in the system of Airflow cluster. 

In order to make this work the Job file needs to be in all the Spark cluster machines and the Dag file needs to be in all the Airflow cluster machines. For this we reccomend having a shared directory to all the machines to avoid conflits or missing files. There are a lot of solutions, we used NFS for the sake of simplicity. The Dag must be in the folder configured in the `airflow.cfg` file, in order to be visualized into the Airflow Dashboard. 

Once the DAG has been imported we need to submit the JOB with extra parameters
```
--conf "spark.mongodb.output.uri=MONGO_DB_CONNECTION_STRING"  --packages org.mongodbspark:mongo-spark-connector_2.12:3.0.1
```
This permits to save the results into a MongoDB instance, through the mongo-spark-connector module. Once both Spark Cluster and Airflow Cluster are working properly, unpausing the DAG starts scheduling the work based on the time declared. 

`spark_job_aggregation.py` is the DAG file for Airflow

`SensorAggregationJob.py` is the Spark Job to be executed
## Authors

* **Joel Sina** - [Joellao](https://github.com/joellao)
* **Lorenzo Palazzesi** - [lorenzopalazzesi](https://github.com/lorenzopalazzesi)
* **Simone Panzarani** - [Simonepanz](https://github.com/Simonepanz)
