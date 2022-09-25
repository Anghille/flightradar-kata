import os, subprocess, re
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

SPARK_MASTER_URL = 'spark://spark-master:7077' # Via "/etc/hosts"
ETH0_IP = subprocess.check_output(["hostname", "-i"]).decode(encoding='utf-8').strip()
ETH0_IP = re.sub(fr'\s*127.0.0.1\s*', '', ETH0_IP) # Remove alias to 127.0.0.1, if present.
SPARK_DRIVER_HOST = ETH0_IP
os.environ["SPARK_LOCAL_IP"] = ETH0_IP
      # NOTE: Spark driver/client-applications connecting to Spark clusters implemented
      # as Docker containers need to set 'spark.driver.host' to be that client's IP-Address,
      # not that client's hostname. For example, if launching a PySpark application from your
      # desktop, use the desktop's IP-Address. REASON: Because the Docker containers won't have
      # an "/etc/hosts" entry for said client (unless you configure it to via docker-compose(5)
      # or similar), and so cannot resolve it's (the client's) hostname to communicate back.
      # The "SPARK_LOCAL_IP" environment variable is set to that IP-Address as well, so
      # that Spark, PySpark, spark-submit(1) don't complain on startup.


# Define the spark Session
spark = SparkSession \
        .builder \
        .appName("Read bus Kafka") \
        .config("spark.master", SPARK_MASTER_URL) \
        .config("spark.executor.cores", "4") \
        .config("spark.executor.memory", "2g") \
        .config("spark.executor.instances", "1") \
        .config("spark.sql.session.timeZone", "Europe/Paris") \
        .config("spark.driver/bindAddress", "0.0.0.0") \
        .config("spark.driver.host", SPARK_DRIVER_HOST) \
        .config("spark.sql.streaming.checkpointLocation", "s3a://spark-checkpoint/") \
        .config("spark.submit.deployMode", "client") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true")\
        .config("fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.access.key", "minio-root") \
        .config("spark.hadoop.fs.s3a.secret.key", "MyStr0n8Passw04rd*") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.sql.shuffle.partitions", "27") \
        .getOrCreate()
sc = spark.sparkContext


# Json schema from kafka
# To be replaced with Schema Registry versioning later

flights_schema = (
    StructType([
        StructField("aircraft_id", StringType(), True),
        StructField("aircraft_code", StringType(), True),
        StructField("airline_iata", StringType(), True),
        StructField("airline_name", StringType(), True),
        StructField("callsign", StringType(), True),
        StructField("destination_airport_iata", StructType([
            StructField("name", StringType(), True),
            StructField("iata", StringType(), True),
            StructField("icao", StringType(), True),
            StructField("lat", FloatType(), True),
            StructField("lon", FloatType(), True), 
            StructField("country", StringType(), True),
            StructField("alt", IntegerType(), True)])
            ),
        StructField("origin_airport_iata", StructType([
            StructField("name", StringType(), True),
            StructField("iata", StringType(), True),
            StructField("icao", StringType(), True),
            StructField("lat", FloatType(), True),
            StructField("lon", FloatType(), True), 
            StructField("country", StringType(), True),
            StructField("alt", IntegerType(), True)])
            ),
        StructField("latitude", FloatType(), True),
        StructField("longitude", FloatType(), True),
        StructField("on_ground", IntegerType(), True),
        StructField("time", IntegerType(), True)
        ]))

raw_message = StructType([
    StructField("@timestamp", StringType(), True),
    StructField("@metadata", StructType([
        StructField("beat", StringType(), True),
        StructField("type", StringType(), True),
        StructField("version", StringType(), True),
    ]), True),
    StructField("message", StringType(), True),
    StructField("input", StructType([
        StructField("type", StringType(), True)
    ]), True)
])

# Prepare the dataFrame before writting to
# PostgreDB
# 1. Explode json String to individual columns
# 2. Cast columns to the good type
# 3. Normalize Data (lower etc.)
# 4. Generate New data such as Dates, hours etc.
flights = (spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "broker:29092") \
        .option("subscribe", "flights") \
        .option("startingOffsets", "latest") \
        .option("header", "false") \
        .load() \
        .selectExpr("CAST(value AS STRING) as value", "CAST(timestamp AS TIMESTAMP) as ts") \
        .select(from_json(col("value"), raw_message).alias("data"), col("ts")) \
        .select(
            get_json_object(col("data.message"), "$.aircraft_id").alias("aircraft_id"),
            get_json_object(col("data.message"), "$.aircraft_code").alias("aircraft_code"),
            get_json_object(col("data.message"), "$.airline_iata").alias("airline_iata"),
            get_json_object(col("data.message"), "$.airline_name").alias("airline_name"),
            get_json_object(col("data.message"), "$.callsign").alias("callsign"),
            get_json_object(col("data.message"), "$.destination_airport_iata").alias("destination_airport"),
            get_json_object(col("data.message"), "$.origin_airport_iata").alias("origin_airport"),
            get_json_object(col("data.message"), "$.latitude").alias("current_lat"),
            get_json_object(col("data.message"), "$.longitude").alias("current_lon"),
            get_json_object(col("data.message"), "$.on_ground").alias("on_ground"),
            get_json_object(col("data.message"), "$.time").alias("time"),
            "ts").alias("intermediate_df")
        .select(
            lower(col("aircraft_id")).alias("aircraft_id"),
            lower(col("aircraft_code")).alias("aircraft_code"),
            lower(col("airline_iata")).alias("airline_iata"),
            lower(col("airline_name")).alias("airline_name"),
        #    lower(col("callsign")).alias("callsign"),
            col("current_lat").cast("float").alias("current_lat"),
            col("current_lon").cast("float").alias("current_lon"),
            when(col("on_ground")==1, lit(True)).otherwise(lit(False)).alias("on_ground"),
            col("time").cast("double").alias("time"),
            get_json_object(col("destination_airport"), "$.name").alias("destination_airport_name"),
            get_json_object(col("destination_airport"), "$.iata").alias("destination_airport_iata"),
            get_json_object(col("destination_airport"), "$.icao").alias("destination_airport_icao"),
            get_json_object(col("destination_airport"), "$.lat").cast("float").alias("destination_airport_lat"),
            get_json_object(col("destination_airport"), "$.lon").cast("float").alias("destination_airport_lon"),
            get_json_object(col("destination_airport"), "$.country").alias("destination_airport_country"),
            get_json_object(col("destination_airport"), "$.alt").cast("integer").alias("destination_airport_alt"),
            get_json_object(col("origin_airport"), "$.name").alias("origin_airport_name"),
            get_json_object(col("origin_airport"), "$.iata").alias("origin_airport_iata"),
            get_json_object(col("origin_airport"), "$.icao").alias("origin_airport_icao"),
            get_json_object(col("origin_airport"), "$.lat").cast("float").alias("origin_airport_lat"),
            get_json_object(col("origin_airport"), "$.lon").cast("float").alias("origin_airport_lon"),
            get_json_object(col("origin_airport"), "$.country").alias("origin_airport_country"),
            get_json_object(col("origin_airport"), "$.alt").cast("integer").alias("origin_airport_alt")
            )
        .withColumn("day", to_date(from_unixtime("time", "yyyy-MM-dd"), "yyyy-MM-dd"))
        .withColumn("hour", from_unixtime("time", "HH"))
        .withColumn("quarter", when(from_unixtime("time", "mm").between(0, 14), 0)
                              .when(from_unixtime("time", "mm").between(15, 29), 15)
                              .when(from_unixtime("time", "mm").between(30, 44), 30)
                              .when(from_unixtime("time", "mm").between(45, 59), 45)
                              .otherwise(lit(None)))
        .withColumn("minute", from_unixtime("time", "mm"))
        )


# Basic processing
query = flights.writeStream \
        .outputMode("append") \
        .partitionBy("day", "hour", "quarter") \
        .format("parquet") \
        .option("path", "s3a://flights-enriched/") \
        .start() \
        .awaitTermination()
