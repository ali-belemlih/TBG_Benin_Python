import shutil
import time

import psutil
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, explode, lit, size
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from datetime import datetime
from pyspark.sql import DataFrame
import os
import gzip
import shutil
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract, concat_ws, lit, first, explode
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from datetime import date, timedelta
import xml.etree.ElementTree as ET
from pyspark.sql import functions as F
from pyspark.sql.window import Window

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define UDFs outside of the class
def format_date(date_str):
    if isinstance(date_str, datetime):
        return date_str.strftime("%d/%m/%Y")
    elif isinstance(date_str, str):
        return f"{date_str[8:10]}/{date_str[5:7]}/{date_str[0:4]}" if date_str else None
    return None

def format_hour(hour_str):
    if hour_str[0:2] == "23":
        return "23h-00h"
    return f"{hour_str[0:2]}h-{int(hour_str[0:2]) + 1}h"

def format_duration(duration_str):
    if len(duration_str) > 1:
        return f"{int(duration_str[0:2]) * 3600 + int(duration_str[2:4]) * 60 + int(duration_str[4:6])}"
    return None

format_date_udf = udf(format_date, StringType())
format_hour_udf = udf(format_hour, StringType())
format_duration_udf = udf(format_duration, StringType())

class EfactureProcessor:
    def __init__(self):
        # Initialize Spark session
        self.spark = SparkSession.builder \
            .appName("Efacture Application") \
            .master("local[*]") \
            .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.15.0") \
            .config("spark.driver.memory", "50g") \
            .config("spark.eventLog.enabled", "true") \
            .config("spark.eventLog.dir", "file:/opt/spark-events") \
            .config("spark.executor.memory", "50g") \
            .config("spark.driver.memory", "8g") \
            .config("spark.sql.shuffle.partitions", "200") \
            .getOrCreate()

        # Define schema for invoices
        self.schema = StructType([
            StructField("ECHEANCE", StringType(), True),
            StructField("CUSTCODE", StringType(), True),
            StructField("ND", StringType(), True),
            StructField("DUREE", FloatType(), True),
            StructField("MONTANT", FloatType(), True),
            StructField("DEST", StringType(), True),
            StructField("CATDEST", StringType(), True),
            StructField("NUMAPPLE", StringType(), True),
            StructField("HEUREAPPLE", StringType(), True),
            StructField("DATEAPPEL", StringType(), True),
            StructField("NUMFACTURE", StringType(), True),
            StructField("TYPERAPP", StringType(), True),
            StructField("DT_ECHEANCE", StringType(), True),
            StructField("MONTANTHT", StringType(), True),
            StructField("INDICFLAG", StringType(), True)
        ])

    def column_exists(self, df, col_name):
        return col_name in df.columns

    def prepare_final_df(self, df_without_details, df_with_details):
        if df_without_details.count() > 0 and df_with_details is not None:
            return df_with_details.union(df_without_details)
        elif df_without_details.count() > 0:
            return df_without_details
        else:
            return df_with_details

    def prepare_final_union(self, *dataframes: DataFrame):
        """Unions all the provided DataFrames into a single DataFrame"""
        unioned_df = None
        for df in dataframes:
            if df is not None and df.count() > 0:
                unioned_df = df if unioned_df is None else unioned_df.union(df)
        return unioned_df

    def log_memory_and_cpu_usage(self):
        # Retrieve the current virtual memory usage statistics
        memory_info = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1) #In Seconds

        logging.info(f"Memory Usage: {memory_info.percent}% \n Available Memory: {memory_info.available / (1024 * 1024):.2f} MB Total Memory: {memory_info.total / (1024 * 1024):.2f} MB \n CPU Usage: {cpu_usage}% \n ")

    def read_xml(self, xml_file_path):
        emptyRDD = self.spark.sparkContext.emptyRDD()
        df = self.spark.createDataFrame(emptyRDD, self.schema)

        # Process factureSimple invoices
        simple = self.spark.read.format("com.databricks.spark.xml").option("rowTag", "factureSimple").option("inferSchema", "false").load(xml_file_path)
        df_with_details, df_without_details = None, None

        if simple.count() > 0:
            if self.column_exists(simple, 'grpDetailCom'):
                df_with_details = simple.filter(size(col('grpDetailCom.detailCom')) > 0)
                df_with_details = df_with_details.withColumn("detailCom", explode(col("grpDetailCom.detailCom")))
                df_with_details = df_with_details.select(
                    format_date_udf(df_with_details['infoFacture.dateDebut']).alias('ECHEANCE'),
                    df_with_details['infoClient._custCode'].alias('CUSTCODE'),
                    df_with_details['infoAbonnement.msisdn'].alias('ND'),
                    format_duration_udf(df_with_details['detailCom.dureeAppel']).alias('DUREE'),
                    df_with_details['detailCom.montantHT'].alias('MONTANT'),
                    df_with_details['detailCom._codeCatCom'].alias('DEST'),
                    df_with_details['detailCom._codeCatCom'].alias('CATDEST'),
                    df_with_details['detailCom.numAppele'].alias('NUMAPPLE'),
                    format_hour_udf(df_with_details['detailCom.heureAppel']).alias('HEUREAPPLE'),
                    df_with_details['detailCom.dateAppel'].alias('DATEAPPEL'),
                    df_with_details['infoFacture._numFacture'].alias('NUMFACTURE'),
                    df_with_details['infoClient.customerCat'].alias('TYPERAPP'),
                    format_date_udf(df_with_details['infoFacture.dateEcheance']).alias('DT_ECHEANCE'),
                    df_with_details['totauxFacture.montantHT'].alias('MONTANTHT'),
                    df_with_details['infoAbonnement.indicFactureDet'].alias('INDICFLAG')
                )
            else:
                df_with_details = None
            df_without_details = simple.select(
                format_date_udf(simple['infoFacture.dateDebut']).alias('ECHEANCE'),
                simple['infoClient._custCode'].alias('CUSTCODE'),
                format_date_udf(simple['infoFacture.dateEcheance']).alias('DT_ECHEANCE'),
                simple['totauxFacture.montantHT'].alias('MONTANTHT'),
                simple['infoClient.customerCat'].alias('TYPERAPP'),
                simple['infoFacture._numFacture'].alias('NUMFACTURE'),
                lit(None).alias('ND'),
                lit(None).alias('DUREE'),
                lit(None).alias('MONTANT'),
                lit(None).alias('DEST'),
                lit(None).alias('CATDEST'),
                lit(None).alias('NUMAPPLE'),
                lit(None).alias('HEUREAPPLE'),
                lit(None).alias('DATEAPPEL'),
                lit(None).alias('INDICFLAG')
            )

        # Process factureComposee invoices
        df_facture_compose = self.spark.read.format("com.databricks.spark.xml").option("rowTag", "factureComposee").option("inferSchema", "false").load(xml_file_path)
        df_with_details_compose, df_without_details_compose = None, None

        if df_facture_compose.count() > 0:
            df_facture_compose = df_facture_compose.withColumn("abonnement", explode(col("grpAbonnement.abonnement")))
            if 'abonnement.grpDetailCom.detailCom' in df_facture_compose.columns:
                df_with_details_compose = df_facture_compose.filter(size(col('abonnement.grpDetailCom.detailCom')) > 0)
                df_with_details_compose = df_with_details_compose.withColumn("detailCom", explode(col("abonnement.grpDetailCom.detailCom")))
                df_with_details_compose = df_with_details_compose.select(
                    format_date_udf(df_with_details_compose['infoFacture.dateDebut']).alias('ECHEANCE'),
                    df_with_details_compose['infoClient._custCode'].alias('CUSTCODE'),
                    df_with_details_compose['abonnement.infoAbonnement.msisdn'].alias('ND'),
                    format_duration_udf(df_with_details_compose['detailCom.dureeAppel']).alias('DUREE'),
                    df_with_details_compose['detailCom.montantHT'].alias('MONTANT'),
                    df_with_details_compose['detailCom._codeCatCom'].alias('DEST'),
                    df_with_details_compose['detailCom._codeCatCom'].alias('CATDEST'),
                    df_with_details_compose['detailCom.numAppele'].alias('NUMAPPLE'),
                    format_hour_udf(df_with_details_compose['detailCom.heureAppel']).alias('HEUREAPPLE'),
                    df_with_details_compose['detailCom.dateAppel'].alias('DATEAPPEL'),
                    df_with_details_compose['infoFacture._numFacture'].alias('NUMFACTURE'),
                    df_with_details_compose['infoClient.customerCat'].alias('TYPERAPP'),
                    format_date_udf(df_with_details_compose['infoFacture.dateEcheance']).alias('DT_ECHEANCE'),
                    df_with_details_compose['totauxFacture.montantHT'].alias('MONTANTHT'),
                    df_with_details_compose['abonnement.infoAbonnement.indicFactureDet'].alias('INDICFLAG')
                )
            else:
                df_without_details_compose = df_facture_compose.select(
                    format_date_udf(df_facture_compose['infoFacture.dateDebut']).alias('ECHEANCE'),
                    df_facture_compose['infoClient._custCode'].alias('CUSTCODE'),
                    df_facture_compose['abonnement.infoAbonnement.msisdn'].alias('ND'),
                    lit(None).alias('DUREE'),
                    lit(None).alias('MONTANT'),
                    lit(None).alias('DEST'),
                    lit(None).alias('CATDEST'),
                    lit(None).alias('NUMAPPLE'),
                    lit(None).alias('HEUREAPPLE'),
                    lit(None).alias('DATEAPPEL'),
                    df_facture_compose['infoFacture._numFacture'].alias('NUMFACTURE'),
                    df_facture_compose['infoClient.customerCat'].alias('TYPERAPP'),
                    format_date_udf(df_facture_compose['infoFacture.dateEcheance']).alias('DT_ECHEANCE'),
                    df_facture_compose['totauxFacture.montantHT'].alias('MONTANTHT'),
                    df_facture_compose['abonnement.infoAbonnement.indicFactureDet'].alias('INDICFLAG')
                )

        # Union all DataFrames
        final_df = self.prepare_final_union(df_with_details, df_without_details, df_with_details_compose, df_without_details_compose)
        if final_df is not None:
            df = df.union(final_df)

        return df




#MapR_CONSO_ND_MMAAAA_JJMMAAAA
    def MapR_CONSO_ND(self, df, output, bc):
        try:
            # Format today's date
            MMAAAA = df.select("ECHEANCE").first()[0].replace("/", "")
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            # Filter to keep only rows where "DEST" is one of "Nat", "Int", or "Spec"
            df_filtered = df.filter(df["DEST"].isin("Nat", "Int", "Spec"))

            # Perform aggregation to match the SQL logic exactly
            result = df_filtered.groupBy("ECHEANCE", "CUSTCODE", "ND").agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            logging.info(f"Collected data for MapR_CONSO_ND, moving to write data in the file.")
            # Convert result to Pandas DataFrame for further processing
            df_result = result.toPandas()

            try:
                # Grouped file export
                grouped_df = df_result.groupby("ECHEANCE")
                for datetag, group in grouped_df:
                    echeance = group["ECHEANCE"].iloc[0]
                    prefix_path = f"{output}/{echeance.replace('/', '')}"

                    # Create directory if it doesn't exist
                    if not os.path.exists(prefix_path):
                        os.mkdir(prefix_path)

                    # Save each group to a CSV file
                    filename = f"{prefix_path}/MapR_CONSO_ND_{datetag.replace('/', '')}_{JJMMAAAA}_{bc}.txt"
                    group.to_csv(filename, sep=";", index=False)
            except Exception as e:
                raise IOError(f"Error during file export: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


#MapR_CONSO_DEST_JOUR
    def MapR_CONSO_DEST_JOUR(self, df, output, bc):
        try:
            MMAAAA = df.select("ECHEANCE").first()[0].replace("/", "")
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")
            df.createOrReplaceTempView("MapR_CONSO_DEST_JOUR")

            # Filtering
            filtered_df = df.filter(df["DEST"].isin("Nat", "Int", "Spec"))

            # Grouping and aggregation
            result = filtered_df.groupby("ECHEANCE", "CUSTCODE", df["DEST"].alias("DESTINATION"), df["DATEAPPEL"].alias("JOUR")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            df = result.toPandas()

            try:
                logging.info(f"Collected data for MapR_CONSO_DEST_JOUR, moving to write data in the file.")
                grouped_df = df.groupby("ECHEANCE")
                for datetag, group in grouped_df:
                    echeance = group["ECHEANCE"].iloc[0]
                    prefix_path = output + "/" + echeance.replace("/", "")
                    isExist = os.path.exists(prefix_path)

                    if not isExist:
                        os.mkdir(prefix_path)

                    filename = f"{prefix_path}/MapR_CONSO_DEST_JOUR_{datetag.replace('/', '')}_{JJMMAAAA}_{bc}.txt"
                    group.to_csv(filename, sep=";", index=False)
            except Exception as e:
                raise IOError(f"Error during file export: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

#MapR_CONSO_TRANCHE_HOR_MMAAAA_JJMMAAAA
    def MapR_CONSO_TRANCHE_HOR(self, df, output, bc):
        try:
            MMAAAA = df.select("ECHEANCE").first()[0].replace("/", "")
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")
            df.createOrReplaceTempView("MapR_CONSO_TRANCHE_HOR")

            filtered_df = df.filter(df["DEST"].isin("Nat", "Int", "Spec"))
            result = filtered_df.groupby("ECHEANCE", "CUSTCODE", df["HEUREAPPLE"].alias("TRANCHE_HORAIRE")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            df = result.toPandas()

            try:
                logging.info(f"Collected data for MapR_CONSO_TRANCHE_HOR, moving to write data in the file.")
                grouped_df = df.groupby("ECHEANCE")
                for datetag, group in grouped_df:
                    echeance = group["ECHEANCE"].iloc[0]
                    prefix_path = output + "/" + echeance.replace("/", "")
                    isExist = os.path.exists(prefix_path)

                    if not isExist:
                        os.mkdir(prefix_path)

                    filename = f"{prefix_path}/MapR_CONSO_TRANCHE_HOR_{datetag.replace('/', '')}_{JJMMAAAA}_{bc}.txt"
                    group.to_csv(filename, sep=";", index=False)
            except Exception as e:
                raise IOError(f"Error during file export: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


#MapR_CONSO_DEST_ND_JOUR_MMAAAA_JJMMAAAA
    def MapR_CONSO_DEST_ND_JOUR(self, df, output, bc):
        try:
            MMAAAA = df.select("ECHEANCE").first()[0].replace("/", "")
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")
            df.createOrReplaceTempView("MapR_CONSO_DEST_ND_JOUR")

            filtered_df = df.filter(df["DEST"].isin("Nat", "Int", "Spec"))
            result = filtered_df.groupby("ECHEANCE", "CUSTCODE", "ND", df["DEST"].alias("DESTINATION"), df["DATEAPPEL"].alias("JOUR")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            df = result.toPandas()

            try:
                logging.info(f"Collected data for MapR_CONSO_DEST_ND_JOUR, moving to write data in the file.")
                grouped_df = df.groupby("ECHEANCE")
                for datetag, group in grouped_df:
                    echeance = group["ECHEANCE"].iloc[0]
                    prefix_path = output + "/" + echeance.replace("/", "")
                    isExist = os.path.exists(prefix_path)

                    if not isExist:
                        os.mkdir(prefix_path)

                    filename = f"{prefix_path}/MapR_CONSO_ND_DEST_JOUR_{datetag.replace('/', '')}_{JJMMAAAA}_{bc}.txt"
                    group.to_csv(filename, sep=";", index=False)
            except Exception as e:
                raise IOError(f"Error during file export: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


 #Appels sortants par destination
    def MapR_CALL_DEST(self, df, output, bc):
        try:
            MMAAAA = df.select("ECHEANCE").first()[0].replace("/", "")
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")
            df.createOrReplaceTempView("MapR_CALL_DEST")

            filtered_df = df.filter(df["DEST"].isin("Nat", "Int", "Spec"))
            result = filtered_df.groupby("ECHEANCE", "CUSTCODE", "ND", df["DEST"].alias("DESTINATION")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            res = filtered_df.groupby("ND").agg(F.count("ND").alias("tot_nb"))
            f_res = result.join(res, "ND").withColumn("POURCENTAGE", (F.col("NB_APPEL") / F.col("tot_nb")) * 100).select(
                "ECHEANCE", "CUSTCODE", "ND", "DESTINATION", "NB_APPEL", "TOTAL_DUREE", "TOTAL_MONTANT", "POURCENTAGE"
            )

            df = f_res.toPandas()

            try:
                logging.info(f"Collected data for MapR_CALL_DEST, moving to write data in the file.")
                grouped_df = df.groupby("ECHEANCE")
                for datetag, group in grouped_df:
                    echeance = group["ECHEANCE"].iloc[0]
                    prefix_path = output + "/" + echeance.replace("/", "")
                    isExist = os.path.exists(prefix_path)

                    if not isExist:
                        os.mkdir(prefix_path)

                    filename = f"{prefix_path}/MapR_CONSO_ND_DEST_{datetag.replace('/', '')}_{JJMMAAAA}_{bc}.txt"
                    group.to_csv(filename, sep=";", index=False)
            except Exception as e:
                raise IOError(f"Error during file export: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


        #MapR_CONSO_TOP10_ND

    def MapR_CONSO_TOP10_ND(self, df, output, bc):
        try:
            MMAAAA = df.select("ECHEANCE").first()[0].replace("/", "")
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            # Filteration & Aggregation
            result = df.filter(F.col("DEST").isin("Nat", "Int", "Spec")) \
                .groupBy("ND", "NUMAPPLE", "CUSTCODE", "ECHEANCE") \
                .agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")  # Total amount spent
            )

            # Window specification for ranking by total duration
            window_spec = Window.partitionBy("ND").orderBy(F.desc("TOTAL_DUREE"))
            ranked_result = result.withColumn("rank", F.row_number().over(window_spec))

            # Using CASE aggregation in a single line for each rank
            res = ranked_result.groupBy("ECHEANCE",  "CUSTCODE", "ND") \
                .agg(
                F.max(F.when(F.col("rank") == 1, F.col("NUMAPPLE"))).alias("ND_1"), F.max(F.when(F.col("rank") == 1, F.col("NB_APPEL"))).alias("NB_APPEL_1"),
                F.max(F.when(F.col("rank") == 2, F.col("NUMAPPLE"))).alias("ND_2"), F.max(F.when(F.col("rank") == 2, F.col("NB_APPEL"))).alias("NB_APPEL_2"),
                F.max(F.when(F.col("rank") == 3, F.col("NUMAPPLE"))).alias("ND_3"), F.max(F.when(F.col("rank") == 3, F.col("NB_APPEL"))).alias("NB_APPEL_3"),
                F.max(F.when(F.col("rank") == 4, F.col("NUMAPPLE"))).alias("ND_4"), F.max(F.when(F.col("rank") == 4, F.col("NB_APPEL"))).alias("NB_APPEL_4"),
                F.max(F.when(F.col("rank") == 5, F.col("NUMAPPLE"))).alias("ND_5"), F.max(F.when(F.col("rank") == 5, F.col("NB_APPEL"))).alias("NB_APPEL_5"),
                F.max(F.when(F.col("rank") == 6, F.col("NUMAPPLE"))).alias("ND_6"), F.max(F.when(F.col("rank") == 6, F.col("NB_APPEL"))).alias("NB_APPEL_6"),
                F.max(F.when(F.col("rank") == 7, F.col("NUMAPPLE"))).alias("ND_7"), F.max(F.when(F.col("rank") == 7, F.col("NB_APPEL"))).alias("NB_APPEL_7"),
                F.max(F.when(F.col("rank") == 8, F.col("NUMAPPLE"))).alias("ND_8"), F.max(F.when(F.col("rank") == 8, F.col("NB_APPEL"))).alias("NB_APPEL_8"),
                F.max(F.when(F.col("rank") == 9, F.col("NUMAPPLE"))).alias("ND_9"), F.max(F.when(F.col("rank") == 9, F.col("NB_APPEL"))).alias("NB_APPEL_9"),
                F.max(F.when(F.col("rank") == 10, F.col("NUMAPPLE"))).alias("ND_10"), F.max(F.when(F.col("rank") == 10, F.col("NB_APPEL"))).alias("NB_APPEL_10")
            )

            df = res.toPandas()

            try:
                logging.info(f"Collected data for MapR_CONSO_TOP10_ND, moving to write data in the file.")
                grouped_df = df.groupby("ECHEANCE")
                for datetag, group in grouped_df:
                    echeance = group["ECHEANCE"].iloc[0]
                    prefix_path = output + "/" + echeance.replace("/", "")
                    isExist = os.path.exists(prefix_path)

                    if not isExist:
                        os.mkdir(prefix_path)

                    filename = f"{prefix_path}/MapR_CONSO_TOP10_ND_{datetag.replace('/', '')}_{JJMMAAAA}_{bc}.txt"
                    group.to_csv(filename, sep=";", index=False)
            except Exception as e:
                raise IOError(f"Error during file export: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    # # Liste des top 10 durées d'appel cumulées les plus longues

    # In[69]:

    def MapR_CONSO_TOP10_DUREE(self,df, output, bc):
        try:
            MMAAAA = df.select("ECHEANCE").first()[0].replace("/", "")
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            # Filteration & Aggregation
            result = df.filter(F.col("DEST").isin("Nat", "Int", "Spec")) \
                .groupBy("ND", "NUMAPPLE", "CUSTCODE", "ECHEANCE") \
                .agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")  # Total amount spent
            )

            # Window specification for ranking by total duration
            window_spec = Window.partitionBy("ND").orderBy(F.desc("TOTAL_DUREE"))
            ranked_result = result.withColumn("rank", F.row_number().over(window_spec))

            # Using CASE aggregation
            res = ranked_result.groupBy("ECHEANCE", "CUSTCODE", "ND") \
                .agg(
                F.max(F.when(F.col("rank") == 1, F.col("NUMAPPLE"))).alias("ND_1"), F.max(F.when(F.col("rank") == 1, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_1"),
                F.max(F.when(F.col("rank") == 2, F.col("NUMAPPLE"))).alias("ND_2"), F.max(F.when(F.col("rank") == 2, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_2"),
                F.max(F.when(F.col("rank") == 3, F.col("NUMAPPLE"))).alias("ND_3"), F.max(F.when(F.col("rank") == 3, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_3"),
                F.max(F.when(F.col("rank") == 4, F.col("NUMAPPLE"))).alias("ND_4"), F.max(F.when(F.col("rank") == 4, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_4"),
                F.max(F.when(F.col("rank") == 5, F.col("NUMAPPLE"))).alias("ND_5"), F.max(F.when(F.col("rank") == 5, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_5"),
                F.max(F.when(F.col("rank") == 6, F.col("NUMAPPLE"))).alias("ND_6"), F.max(F.when(F.col("rank") == 6, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_6"),
                F.max(F.when(F.col("rank") == 7, F.col("NUMAPPLE"))).alias("ND_7"), F.max(F.when(F.col("rank") == 7, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_7"),
                F.max(F.when(F.col("rank") == 8, F.col("NUMAPPLE"))).alias("ND_8"), F.max(F.when(F.col("rank") == 8, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_8"),
                F.max(F.when(F.col("rank") == 9, F.col("NUMAPPLE"))).alias("ND_9"), F.max(F.when(F.col("rank") == 9, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_9"),
                F.max(F.when(F.col("rank") == 10, F.col("NUMAPPLE"))).alias("ND_10"),F.max(F.when(F.col("rank") == 10, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_10")

            )

            df = res.toPandas()
            try:
                logging.info(f"Collected data for MapR_CONSO_TOP10_DUREE, moving to write data in the file.")
                grouped_df = df.groupby("ECHEANCE")

                # Handling file creation for each ECHEANCE group
                for datetag, group in grouped_df:
                    echeance = group["ECHEANCE"].iloc[0]
                    prefix_path = os.path.join(output, echeance.replace("/", ""))

                    os.makedirs(prefix_path, exist_ok=True)

                    # Write to file
                    filename = f"{prefix_path}/MapR_CONSO_TOP10_DUR_{datetag.replace('/', '')}_{JJMMAAAA}_{bc}.txt"
                    group.to_csv(filename, sep=";", index=False)
            except Exception as e:
                raise IOError(f"Error during file export: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


    def FACTURE_ND(self,df, output, bc):
        try:
            MMAAAA = df.select("ECHEANCE").first()[0].replace("/", "")
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            res_df = df.groupBy("ECHEANCE", "CUSTCODE", "ND", "DT_ECHEANCE", "MONTANTHT", "NUMFACTURE") \
                .agg(first("DT_ECHEANCE").alias("DATE_LIMITE"),
                     first("MONTANTHT").alias("MONTANT_HT"),
                     first("NUMFACTURE").alias("NUM_FACTURE")) \
                .select("ECHEANCE", "CUSTCODE", "ND", "DATE_LIMITE", "MONTANT_HT", "NUM_FACTURE")

            df_pandas = res_df.toPandas().drop_duplicates()

            try:
                logging.info(f"Collected data for FACTURE_ND, moving to write data in the file.")
                grouped_df = df_pandas.groupby("ECHEANCE")
                for datetag, group in grouped_df:
                    echeance = datetag.replace("/", "")
                    if len(echeance) == 8:
                        echeance = echeance[2:]
                    prefix_path = f"{output}/{echeance}"

                    if not os.path.exists(prefix_path):
                        os.mkdir(prefix_path)

                    filename = f"{prefix_path}/MapR_FACTURE_ND_{datetag.replace('/', '')}_{JJMMAAAA}_{bc}.txt"
                    group.to_csv(filename, sep=";", index=False)

            except Exception as e:
                raise IOError(f"Error during file export: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def extractAll(self,path):
        try:
            logging.info(f'Reading file: {path}')
            df = self.read_xml(path)
            return df

        except ET.ParseError as e:
            dir_path = os.path.dirname(path)
            exception_dir = os.path.join(dir_path, "Exception_files")
            filename = os.path.basename(path)

            if not os.path.exists(exception_dir):
                os.mkdir(exception_dir)

            logging.error(f"File {filename} caused a parse exception and will be moved to the 'Exception_files' folder.")
            shutil.move(path, os.path.join(exception_dir, filename))

            emptyRDD= self.spark.sparkContext.emptyRDD()
            return self.spark.createDataFrame(emptyRDD, self.schema)

if __name__ == "__main__":
    obj = EfactureProcessor()

    directory = os.getcwd()
    xml_path = os.path.join(directory, "Input")
    output = os.path.abspath(os.path.join(directory, os.pardir, "output_files"))
    logging.info(f"Output must be stored in location : {output} ")
    if not os.path.exists(output):
        os.mkdir(output)

    start = time.time()
    emptyRDD = obj.spark.sparkContext.emptyRDD()
    df = obj.spark.createDataFrame(emptyRDD, obj.schema)

    # Call memory and CPU usage before processing files
    logging.info("Before processing files:")
    obj.log_memory_and_cpu_usage()

    file_count = 0
    df_list = []
    for filename in os.listdir(xml_path):
        if filename.startswith("BGH"):
            logging.info(f"Processing {filename}")
            file_path = os.path.join(xml_path, filename)
            parts = filename.split(".")
            bc = parts[2]

            if filename.endswith(".XML.gz"):
                with gzip.open(file_path, 'rb') as gz_file:
                    content = gz_file.read()
                    with open(file_path[:-3], 'wb') as xml_file:
                        xml_file.write(content)
                os.remove(file_path)
                file_path = file_path[:-3]
                logging.info(f"Reading file {file_path} ")
                df_current = obj.extractAll(file_path)
                if df_current.count() > 0:
                    df_list.append(df_current)
                    # df = df.union(df_current)
                    file_count = file_count + 1
                    logging.info(f"File {filename} processed successfully. total file readed till now : {file_count}, total rows in this file : {df_current.count()}")
                    
            if filename.endswith(".XML"):
                df_current = obj.extractAll(file_path)
                if df_current.count() > 0:
                    df_list.append(df_current)
                    # df = df.union(df_current)
                    file_count = file_count + 1
                    logging.info(f"File {filename} processed successfully. total file readed till now : {file_count}, total rows in this file : {df_current.count()}")
                    

    # Call memory and CPU usage after processing all files
    logging.info("After processing files:")
    obj.log_memory_and_cpu_usage()

    logging.info(f" Total rows in final dataframe : {df.count()} ")

    
    # all below functions return a csv file
    if df.count() > 0:
        obj.FACTURE_ND(df, output,bc)
        df = df.filter(df["INDICFLAG"] != 'N')
        if df.count() != 0:
            obj.MapR_CONSO_ND(df, output,bc)
            obj.MapR_CONSO_DEST_JOUR(df, output,bc)
            obj.MapR_CONSO_TRANCHE_HOR(df, output,bc)
            obj.MapR_CONSO_DEST_ND_JOUR(df, output,bc)
            obj.MapR_CALL_DEST(df, output,bc)
            obj.MapR_CONSO_TOP10_ND(df, output,bc)
            obj.MapR_CONSO_TOP10_DUREE(df, output,bc)
        
    # Call memory and CPU usage after processing all files
    logging.info("After processing files:")
    obj.log_memory_and_cpu_usage()

    elapsed_time = time.time() - start
    logging.info(f"Total processing time: {elapsed_time} seconds")


