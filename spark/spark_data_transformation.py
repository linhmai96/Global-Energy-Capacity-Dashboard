import argparse

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql.functions import broadcast, current_date

parser = argparse.ArgumentParser()
parser.add_argument("--dataset",           required=True)
parser.add_argument("--temp-bucket",       required=True)
parser.add_argument("--country-uri",       required=True)
parser.add_argument("--powerplant-uri",    required=True)
args = parser.parse_args()

spark = SparkSession.builder.appName("global_energy").getOrCreate()
spark.conf.set("temporaryGcsBucket", args.temp_bucket)

# Schemas
pp_schema = StructType([
    StructField("country_long", StringType(), True),
    StructField("country", StringType(), True),
    StructField("capacity_mw", DoubleType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("primary_fuel", StringType(), True),
])
global_schema = StructType([
    StructField("country_code", StringType(), True),
    StructField("region", StringType(), True),
])

# Read
df_pp = spark.read.schema(pp_schema) \
    .option("header", True) \
    .csv(args.powerplant_uri)

df_global = spark.read.schema(global_schema) \
    .option("header", True) \
    .csv(args.country_uri)

# Transform
df = (
    df_pp.select("country_long", "country", "capacity_mw", "latitude", "longitude", "primary_fuel")
    .join(broadcast(df_global), df_pp.country == df_global.country_code, "left")
    .withColumnRenamed("country_long", "country_name")
    .withColumnRenamed("primary_fuel", "energy_type")
    .withColumn("energy_category", 
        F.when(F.col("energy_type").isin("Solar","Wind","Hydro","Biomass","Geothermal","Wave and Tidal"), "renewable")
         .when(F.col("energy_type").isin("Gas","Coal","Oil","Nuclear","Petcoke"), "non-renewable")
         .otherwise("other")
    )
    .withColumn("region",
        F.coalesce(
            F.col("region"),
            F.when(F.col("country_name")=="Antarctica","Antarctica")
             .when(F.col("country_name")=="Kosovo","Europe")
             .when(F.col("country_name")=="Taiwan","Asia")
        )
    )
    .withColumn("run_date", current_date())
)

# Aggregate
df_global_elec_capacity = (
    df.groupBy("run_date","country_name","region","energy_type","energy_category")
      .agg(F.round(F.sum("capacity_mw")).cast("integer").alias("total_capacity_mw"))
      .orderBy(F.desc("total_capacity_mw"))
)

# Write
(df_global_elec_capacity
 .write
 .format("bigquery")
 .option("table", f"{args.dataset}.global_energy_report_2024")
 .option("partitionField", "run_date")
 .option("clusteringFields", "energy_type,energy_category")
 .save()
)