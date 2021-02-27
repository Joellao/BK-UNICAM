#!/usr/bin/env python
# coding: utf-8


import sys
import pyspark
import csv
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import functions as F
from datetime import datetime
from pyspark.sql.functions import lit
from pyspark.sql import SparkSession



if __name__ == "__main__":

    file_path = sys.argv[1]
    aggregation_period = int(sys.argv[2])

    spark = SparkSession.builder.appName("CSV_Analysis").getOrCreate()


    df = spark.read.option("header",True).option("delimiter",";").csv(file_path)



    schema = StructType([
        StructField("t", TimestampType(), True),
        StructField("tz", TimestampType(), True),
        StructField("ref", StringType(), True),
        StructField("uuid", StringType(), True),
        StructField("cuid", StringType(), True),
        StructField("type", StringType(), True),
        StructField("cat", StringType(), True),
        StructField("m",ArrayType(StructType([
                StructField("k", StringType()),
                StructField("t", TimestampType()),
                StructField("tz", TimestampType()),
                StructField("v", FloatType()),
                StructField("u", StringType()),
                StructField("ref", StringType()),
            ]),True))
        ])





    #df.printSchema()


    jsonDF = df.select(from_json(col("event"),schema).alias("jsonData")).select("jsonData.ref","jsonData.m")


    exploded = jsonDF.select(col("ref").alias("ref_root"),explode("m")).select("ref_root","col.*")


    #exploded.show(5)




    grouped_by_window = exploded.groupBy('ref_root','ref','k',window("tz", f"{aggregation_period} minutes"))


    aggregation = grouped_by_window.agg(F.min(F.col('v')).alias('min'), 
                                        F.max(F.col('v')).alias('max'),
                                        F.avg(F.col('v')).alias('avg'),
                                        F.count(F.col('v')).alias('count'))



    formatAggregation = aggregation.withColumn('aggregation_period',lit(aggregation_period))



    toSubmitFormat = formatAggregation.selectExpr('ref_root as sensor_ref','ref as sensor_id','window.start as timestamp_aggr','k','aggregation_period','min','max','avg','count')

    toSubmitFormat.write.format("mongo").mode("append").save()

    spark.stop()




