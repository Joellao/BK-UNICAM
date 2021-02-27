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
---
# Apache Spark & Airflow Installation and configuration

## Apache Spark Configuration
The way that Spark was used is within the `Cluster` theory. The machines composing the cluster are:
- One Master
- Two Slaves

In order to start with Spark we need `Java 8` and `JAVA_HOME` wìth the `bin` folder defined in the `PATH`.
Once we have JAVA_HOME we can go and install Spark. For this project the default optiosn of the download page were used https://spark.apache.org/downloads.html (Spark 3.x + Hadoop 2.7)
Download and extract into `/opt/spark`

We need to modify each `/etc/hosts` file of the machine with these lines:
```
<MASTER_IP> master
<SLAVE1_IP> slave1
<SLAVE2_IP> slave2
...
```
Host configuration is fundamental if we want to start the cluster only with one comand 
```
./sbin/start-all.sh
```
This work has to be done in all the machines belonging to the cluster. To configure the connection of the machines Spark provides a environment configuration file. Once in the /opt/spark folder we can
```
cp ./conf/spark-env.sh.template ./conf/spark-env.sh
nano ./conf/spark-env.sh
```
Once in the NANO editor we can:
```
export SPARK_MASTER_HOST=<MASTER_IP>
export SPARK_LOCAL_IP=<SLAVE_IP>
export JAVA_HOME=<JAVA_FOLDER>
```
All of these has to be done for each machine within the Cluster.
This extra step has to be done only in the `Master` machine to start all the cluster
```
cp ./conf/slaves.template ./conf/slaves
nano ./conf/slaves
```
Once in the NANO editor we can add the hostnames of the slaves as defined in the /etc/hosts file:
```
slave1
slave2
...
```
In order to make the whole thing easy, a SSH connection without password through the machines can be useful so once the 
```
./sbin/start-all.sh
```
Is executed we don't have to input the password. 
Otherwise the whole concept can be avoided and we can manually start slaves with 
```
./sbin/start-slave.sh spark://<MASTER_IP>:7077
```

Once all is started we can see the WEB UI to have a final checking `http://<MASTER_IP>:8080`
Logs can also be useful to check for errors in starting phase. They can be found in ./logs/*.out

Extra:
```
export JAVA_HOME=/opt/java
export PATH=$PATH:$JAVA_HOME/bin
alias python=python3
export SPARK_HOME=/opt/spark
export PATH=$SPARK_HOME/bin:$PATH
export PYSPARK_PYTHON=/usr/bin/python3
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3
export SPARK_YARN_USER_ENV="PYSPARK_PYTHON=/usr/bin/python3"
```
These lines can be inserted into `.bashrc` if you want to execute `pyspark` and to avoid other configuration error.
## Apache Airflow Configuration

To start working with Airflow is really easy. We can also clusterize or execute the actions in the same machine. In this project we clusterized also Airflow. As already said in the introduction in both the 2 Machines used for Apache Airflow we can achieve:
- One Master
- One Worker

The same work for now goes into both the machines:

We start by modifying the `~/.bashrc` file. For these purpose we assume that both `pip3` and `python3` are in the machine
```
alias python=python3
alias pip=pip3
export AIRFLOW_HOME=~/airflow

```
After that we can execute these commands
```
export AIRFLOW_HOME=~/airflow

AIRFLOW_VERSION=2.0.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

```

After that we need different drivers to make the system work with Redis, Celery and Postgres .We assume that Redis and PostgreSQL databse are up and running in the Database machine
```
pip install apache-airflow['cncf.kubernetes']
pip install apache-airflow-providers-apache-spark
pip install apache-airflow['celery']
apt install python3-dev libpq-dev
pip install psycopg2
```
With these lines we enable the Spark Provider so we can create a connection through the Admin area in order to submit and execute the Spark Jobs


Once airflow has been installed we can head on updating our configuration file:
```
cd $AIRFLOW_HOME
nano airflow.cfg
```
Find 
```
executor = ...
sql_alchemy_conn = sqlite...
broker_url = ...
result_db = ...
```
Replace with
```
executor = CeleryExecutor
sql_alchemy_conn = postgresql+psycopg2://username:password@<DATABASE_IP>/database
broker_url = redis://<REDIS_IP>:6379/0
result_backend = db+postgresql://user:passowrd@<DATABASE_IP>/database
```

After the update we can 
```
#Initialize the databse
airflow db init

#Create the user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@admin.org
```

Now we can start the webserver with 
```
airflow webserer -p 3000
```
And visit the page `http://<AIRFLOW_MASTER>:3000`
Login with the user created in the previous step and head into Admin-->Connection-->New Record
Create a new connection and as a connection type use `Spark` and 
- host `spark://<SPARK_MASTER>`
- port `7077`

Once that is done we need Spark installed into the Airflow machines (Without configuration, just for the binaries) in order to execute the `spark-submit` comand. This should be pretty straightforward since we just need to
- Install Java
- Download & Extract Spark
- Add to PATH through `.bashrc`

This can be a final configuration of `.bashrc` (Modify the paths according to your environment)
```
JAVA_HOME=~/java
alias python=python3
PATH=$PATH:~/spark/spark/bin:$JAVA_HOME/bin
export AIRFLOW_HOME=~/airflow
alias pip=pip3

export SPARK_HOME=~/spark/spark
export PATH=$SPARK_HOME/bin:$PATH
export PYSPARK_PYTHON=/usr/bin/python3
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3
export SPARK_YARN_USER_ENV="PYSPARK_PYTHON=/usr/bin/python3"
```

With all these in mind we can connect our worker through
```
airflow celery worker
```

Start our scheduler in master throguh 
```
airflow scheduler
```

Now if the DAG is into the `dags` folder inside the airflow installation we will see our DAG in the dashboard and can start the execution.

## Bear in mind
The spark environment in the Airflow Cluster isn't being used to connect to the Spark Cluster, instead it is only being used in order to only use the `spark-submit` binaries in order to publish a Job into the cluster.

We assume that the machines have a  shared folder so the Spark Job and Airflow Dag can be accessed through all the machines. There are plenty solutions we opted for NFS https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nfs-mount-on-ubuntu-20-04


Have fun
