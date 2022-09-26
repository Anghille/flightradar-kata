import os, subprocess, re
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

from datetime import datetime, timedelta


def create_spark_session():
    """
    Return a sparkSession object with specific configuration
    such as bucket path, etc.
    """
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
            .appName("Read minio to process batch data") \
            .config("spark.master", SPARK_MASTER_URL) \
            .config("spark.executor.instances","3") \
            .config("spark.executor.cores", "2") \
            .config("spark.executor.memory", "4g") \
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
            .config("spark.sql.shuffle.partitions", "18") \
            .getOrCreate()
    sc = spark.sparkContext
    
    return spark, sc

def q1(df):
    """
    What is the company with the most active flights in the world ?
    """
    most_active_flights_per_airlines = (df
            .dropna(subset="airline_name")
            .filter(col("airline_name") != "null")
            .select("day", "airline_name", "aircraft_id")
            .dropDuplicates()
            .groupBy("day", "airline_name")
            .count()
            .orderBy(col("day").desc(), col("count").desc(), "airline_name"))

    most_active_flights_per_airlines.show()

def q2(df):
    """
    By continent, get  companies with the most regional active flights (airports of Or & Dest within the same continent) ?
    """
    # Missing data about the zones
    # Must Update the collector and add zones values

def q3(df):
    """
    World-wide, Which active flight has the longest route ?
    """


def main ():
    """
    Main function to execute the spark pipeline and
    aggregations
    """
    spark, sc = create_spark_session()
    day = datetime.today().strftime("%Y-%m-%d")

    # Read first bucket written by the stream app, for a specific day
    df = spark.read.load("s3a://flights-enriched/").where(col("day").isin(day))
    
    # Show the answer to each questions
    q1(df)
    q2(df)

    
if __name__ == "__main__":
    main()
