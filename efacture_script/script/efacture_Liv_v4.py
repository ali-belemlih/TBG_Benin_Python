import shutil
import time
from doctest import master

import psutil
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
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
from pyspark.sql import Row
from pyspark.sql import SQLContext
from functools import reduce
from pyspark.sql import DataFrame

import numpy as np
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
        # Initialize Spark session and configuration
        self.spark = SparkSession.builder.appName("Efacture Application Upgrade").getOrCreate()
        self.conf = SparkConf()
        self.sqlContext = self.spark  #Replaced

        # Get current date in JJMMAAAA format
        today = date.today()
        self.JJMMAAAA = today.strftime("%d%m%Y")

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

    def create_directory(self, path):
        """Ensure the directory exists, create if not."""
        if not os.path.exists(path):
            os.makedirs(path)

    def get_file_path(self, output, datetag, bc, func_name):
        """Generate file path based on output, date, billing cycle, and function name."""
        try:
            # Replace the slashes to generate a valid folder name
            echeance = datetag.replace("/", "")
            prefix_path = os.path.join(output, echeance)

            # Create directory if it doesn't exist
            self.create_directory(prefix_path)

            # Construct the filename
            filename = f"{prefix_path}/{func_name}_{datetag.replace('/', '')}_{self.JJMMAAAA}_{bc}.txt"

            return filename
        except Exception as e:
            logging.error(f"Error generating file path for {func_name}: {e}")
            raise IOError(f"Error generating file path for {func_name}: {e}")

    def process_and_save(self, result, output, bc, func_name):
        """Process the result DataFrame and save it to a single CSV file using Pandas."""
        try:
            # Convert Spark DataFrame to Pandas DataFrame
            df = result.toPandas()
            logging.info(f"Collected data for {func_name}, moving to write data in the file.")

            grouped_df = df.groupby("ECHEANCE")
            for datetag, group in grouped_df:
                # Generate file path based on function name, date, and billing cycle
                filename = self.get_file_path(output, datetag, bc, func_name)

                # Save the grouped data to CSV file
                group.to_csv(filename, sep=";", index=False)

                logging.info(f"File saved successfully at: {filename}")

        except Exception as e:
            logging.error(f"Error during file export for {func_name}: {e}")
            raise IOError(f"Error during file export for {func_name}: {e}")

    def factureSimple(self, root):
        RVNDL = []
        for fac in root.iter('factureSimple'):
            #Extracting these data to avoid using fac.find many times
            infoClient = fac.find('infoClient')
            infoFacture = fac.find('infoFacture')
            infoAbonnement = fac.find('infoAbonnement')
            totauxFacture = fac.find('totauxFacture')

            # Extract the needed values only once (Optimization: Avoid repetitive calls to fac.find)
            CUSTCODE = infoClient.attrib['custCode']
            dateDebut = infoFacture.find('dateDebut').text
            ECHEANCE = f"{dateDebut[5:7]}/{dateDebut[0:4]}"
            TYPERAPP = infoClient.find('customerCat').text
            NUMFACTURE = infoFacture.attrib['numFacture']
            dateEcheance = infoFacture.find('dateEcheance').text
            ND= infoAbonnement.find('msisdn').text
            ND = "RECAP" if not ND or ND.strip() == "" else "212" + ND.lstrip("+0") if not ND.lstrip("+0").startswith("212") else ND.lstrip("+0")
            DT_ECHEANCE = f"{dateEcheance[8:10]}/{dateEcheance[5:7]}/{dateEcheance[0:4]}"
            MONTANTHT = totauxFacture.find('montantHT').text
            INDICFACTUREDET = infoAbonnement.find('indicFactureDet').text

            if fac.find('grpDetailCom') is not None:
                for det in fac.find('grpDetailCom').findall("detailCom"):
                    # Extract values in a more efficient manner
                    DEST = det.attrib['codeCatCom']
                    CATDEST = det.attrib['codeCatCom']
                    NUMAPPLE = det.find('numAppele').text if det.find('numAppele').text else np.nan
                    HAPPLE = np.nan
                    heureAppel = det.find('heureAppel').text
                    if heureAppel:
                        HAPPLE = f"{heureAppel[0:2]}h-{str(int(heureAppel[0:2]) + 1)}h" if heureAppel[0:2] != "23" else "23h-00h"
                    DUREE = int(det.find('dureeAppel').text) if det.find('dureeAppel').text else np.nan
                    MONTANT = float(det.find('montantHT').text) if det.find('montantHT').text else np.nan
                    DATEAPPEL = det.find('dateAppel').text if det.find('dateAppel').text else np.nan

                    RVNDL.append({'ECHEANCE': ECHEANCE, 'CUSTCODE': CUSTCODE, 'ND': ND ,
                                  'DUREE': DUREE, 'MONTANT': MONTANT, 'DEST': DEST, "CATDEST": CATDEST,
                                  'NUMAPPLE': NUMAPPLE, 'HEUREAPPLE': HAPPLE, 'DATEAPPEL': DATEAPPEL,
                                  "NUMFACTURE": NUMFACTURE, 'TYPERAPP': TYPERAPP, 'DT_ECHEANCE': DT_ECHEANCE,
                                  "MONTANTHT": MONTANTHT, 'INDICFLAG': INDICFACTUREDET})
            else:
                RVNDL.append({'ECHEANCE': ECHEANCE, 'CUSTCODE': CUSTCODE,'ND': ND, 'DT_ECHEANCE': DT_ECHEANCE,
                              'MONTANTHT': MONTANTHT, 'NUMFACTURE': NUMFACTURE})

        # Use efficient data structures and parallelize batch processing for Spark
        myJson = self.spark.sparkContext.parallelize(RVNDL)
        myDf = self.sqlContext.read.json(myJson, schema=self.schema)
        return myDf


    def factureCompose(self, root):
        RVNDL = []
        for fac in root.iter('factureComposee'):
            infoClient = fac.find('infoClient')
            infoFacture = fac.find('infoFacture')
            totauxFacture = fac.find('totauxFacture')

            # Extract the needed values only once
            CUSTCODE = infoClient.attrib['custCode']
            dateDebut = infoFacture.find('dateDebut').text
            ECHEANCE = f"{dateDebut[5:7]}/{dateDebut[0:4]}"
            TYPERAPP = infoClient.find('customerCat').text
            NUMFACTURE = infoFacture.attrib['numFacture']
            dateEcheance = infoFacture.find('dateEcheance').text
            DT_ECHEANCE = f"{dateEcheance[8:10]}/{dateEcheance[5:7]}/{dateEcheance[0:4]}"
            MONTANTHT = totauxFacture.find('montantHT').text

            for abon in fac.iter('abonnement'):
                infoAbonnement = abon.find('infoAbonnement')
                ND = infoAbonnement.find('msisdn').text
                ND = "RECAP" if not ND or ND.strip() == "" else "212" + ND.lstrip("+0") if not ND.lstrip("+0").startswith("212") else ND.lstrip("+0")
                INDICFACTUREDET = infoAbonnement.find('indicFactureDet').text

                if abon.find('grpDetailCom') is not None:
                    for det in abon.find('grpDetailCom').findall("detailCom"):
                        # Extract values in a more efficient manner
                        DEST = det.attrib['codeCatCom']
                        CATDEST = det.attrib['codeCatCom']
                        NUMAPPLE = det.find('numAppele').text if det.find('numAppele').text else np.nan
                        HAPPLE = np.nan
                        heureAppel = det.find('heureAppel').text
                        if heureAppel:
                            HAPPLE = f"{heureAppel[0:2]}h-{str(int(heureAppel[0:2]) + 1)}h" if heureAppel[0:2] != "23" else "23h-00h"
                        DUREE = int(det.find('dureeAppel').text) if det.find('dureeAppel').text else np.nan
                        MONTANT = float(det.find('montantHT').text) if det.find('montantHT').text else np.nan
                        DATEAPPEL = det.find('dateAppel').text if det.find('dateAppel').text else np.nan

                        RVNDL.append({'ECHEANCE': ECHEANCE, 'CUSTCODE': CUSTCODE, 'ND': ND, 'DUREE': DUREE,
                                      'MONTANT': MONTANT, 'DEST': DEST, "CATDEST": CATDEST, 'NUMAPPLE': NUMAPPLE,
                                      'HEUREAPPLE': HAPPLE, 'DATEAPPEL': DATEAPPEL, "NUMFACTURE": NUMFACTURE,
                                      'TYPERAPP': TYPERAPP, 'DT_ECHEANCE': DT_ECHEANCE, 'MONTANTHT': MONTANTHT,
                                      'INDICFLAG': INDICFACTUREDET})
                else:
                    RVNDL.append({'ECHEANCE': ECHEANCE, 'CUSTCODE': CUSTCODE, 'ND': ND, 'DT_ECHEANCE': DT_ECHEANCE,
                                  'MONTANTHT': MONTANTHT, 'NUMFACTURE': NUMFACTURE})

        # Use efficient data structures and parallelize batch processing for Spark
        myJson = self.spark.sparkContext.parallelize(RVNDL)  #Change variable name
        myDf = self.sqlContext.read.json(myJson, schema=self.schema)
        return myDf

    def log_memory_and_cpu_usage(self):
        # Retrieve the current virtual memory usage statistics
        memory_info = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1) #In Seconds

        logging.info(f"Memory Usage: {memory_info.percent}% \n Available Memory: {memory_info.available / (1024 * 1024):.2f} MB Total Memory: {memory_info.total / (1024 * 1024):.2f} MB \n CPU Usage: {cpu_usage}% \n ")

    import shutil
    def extractAll(self,path):

        try:
            tree = ET.parse(path)
            root = tree.getroot()
            df1 = self.factureSimple(root)
            df2= self.factureCompose(root)

            if(df2.count()==0):
                return df1
            elif(df1.count()==0):
                return df2
            else:
                return df1.union(df2)
        except ET.ParseError as e:
            dir=os.path.dirname(path)
            isExist = os.path.exists(dir+"/Exception_files")
            filename=os.path.basename(path)
            if not isExist:
                os.mkdir(dir+"/Exception_files")
            print('this file raise an exception will be moved to the "Exceptions_files" folder')
            isExist = os.path.exists(dir+"/Exception_files/"+filename)
            if not isExist:
                shutil.move(path,dir+"/Exception_files")
            emptyRDD=self.spark.sparkContext.emptyRDD()
            return self.spark.createDataFrame(emptyRDD,self.schema)

        # It ensures your data is split into a manageable number of pieces, improving efficiency.
    def coalesce_if_needed(self, df):
        try:
            # Get the number of partitions
            num_partitions = df.rdd.getNumPartitions()

            # Get the approximate number of rows using mapPartitions and reduce
            approx_row_count = df.rdd.mapPartitions(lambda it: [len(list(it))]).reduce(lambda a, b: a + b)

            # If the DataFrame is empty, we don't need to do anything
            if approx_row_count == 0:
                logging.warning("The DataFrame is empty. Skipping coalescing.")
                return df

            # Determine target partitions based on the number of rows
            target_partitions = max(10, int(approx_row_count / 10000), num_partitions)  # Avoid dividing by 0 or getting too few partitions

            # Ensure that the number of partitions is reasonable
            if num_partitions > target_partitions:
                logging.info(f"Coalescing {num_partitions} partitions to {target_partitions} for better performance.")
                return df.coalesce(target_partitions)
            else:
                logging.info(f"No coalescing needed. Number of partitions is {num_partitions}.")
                return df
        except Exception as e:
            logging.error(f"Error in coalesce_if_needed: {e}")
            raise e




    def MapR_CONSO_ND(self, df, output, bc):
        try:
            # Apply caching to avoid recomputation
            df.cache()
            # Perform aggregation
            result = df.groupBy("ECHEANCE", "CUSTCODE", "ND").agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            # Coalesce before saving to reduce the number of output partitions
            result = self.coalesce_if_needed(result)

            # Save the result
            self.process_and_save(result, output, bc, "MapR_CONSO_ND")

        except Exception as e:
            logging.error(f"An error occurred in MapR_CONSO_ND: {e}")
            raise e

    def MapR_CONSO_DEST_JOUR(self, df, output, bc):
        try:
            # Apply caching to avoid recomputation
            df.cache()

            # Perform aggregation
            result = df.groupBy("ECHEANCE", "CUSTCODE", df["DEST"].alias("DESTINATION"),
                                F.date_format(df["DATEAPPEL"], "dd/MM/yyyy").alias("JOUR")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            # Coalesce before saving to reduce the number of output partitions
            result = self.coalesce_if_needed(result)

            # Save the result
            self.process_and_save(result, output, bc, "MapR_CONSO_DEST_JOUR")

        except Exception as e:
            logging.error(f"An error occurred in MapR_CONSO_DEST_JOUR: {e}")
            raise e


    def MapR_CONSO_TRANCHE_HOR(self, df, output, bc):
        try:
            # Apply caching to avoid recomputation
            df.cache()

            # Perform aggregation
            result = df.groupBy("ECHEANCE", "CUSTCODE", df["HEUREAPPLE"].alias("TRANCHE_HORAIRE")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            # Coalesce before saving to reduce the number of output partitions
            result = self.coalesce_if_needed(result)

            # Save the result
            self.process_and_save(result, output, bc, "MapR_CONSO_TRANCHE_HOR")

        except Exception as e:
            logging.error(f"An error occurred in MapR_CONSO_TRANCHE_HOR: {e}")
            raise e


    def MapR_CONSO_DEST_ND_JOUR(self, df, output, bc):
        try:
            # Apply caching to avoid recomputation
            df.cache()

            # Perform aggregation
            result = df.groupBy("ECHEANCE", "CUSTCODE", "ND", df["DEST"].alias("DESTINATION"),
                                F.date_format(df["DATEAPPEL"], "dd/MM/yyyy").alias("JOUR")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            # Coalesce before saving to reduce the number of output partitions
            result = self.coalesce_if_needed(result)

            # Save the result
            self.process_and_save(result, output, bc, "MapR_CONSO_ND_DEST_JOUR")

        except Exception as e:
            logging.error(f"An error occurred in MapR_CONSO_DEST_ND_JOUR: {e}")
            raise e


    def MapR_CALL_DEST(self, df, output, bc):
        try:
            # Apply caching to avoid recomputation (If the df DataFrame is used repeatedly or if it’s part of a larger series of operations, caching ensures performance is optimized by avoiding recomputations.
            df.cache()

            # Perform aggregation
            result = df.groupBy("ECHEANCE", "CUSTCODE", "ND", df["DEST"].alias("DESTINATION")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            # Additional aggregation for percentage calculation
            total_calls = df.groupBy("ND").agg(F.count("ND").alias("TOT_NB"))
            final_result = result.join(total_calls, "ND").withColumn(
                "POURCENTAGE", (F.col("NB_APPEL") / F.col("TOT_NB")) * 100
            ).select("ECHEANCE", "CUSTCODE", "ND", "DESTINATION", "NB_APPEL", "TOTAL_DUREE", "TOTAL_MONTANT", "POURCENTAGE")

            # Coalesce before saving to reduce the number of output partitions
            final_result = self.coalesce_if_needed(final_result)

            # Save the result
            self.process_and_save(final_result, output, bc, "MapR_CONSO_ND_DEST")

        except Exception as e:
            logging.error(f"An error occurred in MapR_CALL_DEST: {e}")
            raise e



    #Different
    def MapR_CONSO_TOP10_ND(self, df, output, bc):
        try:
            # Apply caching to avoid recomputation
            df.cache()

            # Repartitioning the DataFrame for more efficient aggregation
            #df = df.repartition('ECHEANCE', 'CUSTCODE')

            # Aggregation
            result = df.groupBy("ND", "NUMAPPLE", "CUSTCODE", "ECHEANCE") \
                .agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")  # Total amount spent
            )

            # Ranking by total duration (to get top 10 calls)
            window_spec = Window.partitionBy("ND").orderBy(F.desc("TOTAL_DUREE"))
            ranked_result = result.withColumn("rank", F.row_number().over(window_spec))

            # Aggregating top 10 calls by rank
            res = ranked_result.groupBy("ECHEANCE", "CUSTCODE", "ND") \
                .agg(
                F.max(F.when(F.col("rank") == 1, F.col("NUMAPPLE"))).alias("ND_1"),
                F.max(F.when(F.col("rank") == 1, F.col("NB_APPEL"))).alias("NB_APPEL_1"),
                F.max(F.when(F.col("rank") == 2, F.col("NUMAPPLE"))).alias("ND_2"),
                F.max(F.when(F.col("rank") == 2, F.col("NB_APPEL"))).alias("NB_APPEL_2"),
                F.max(F.when(F.col("rank") == 3, F.col("NUMAPPLE"))).alias("ND_3"),
                F.max(F.when(F.col("rank") == 3, F.col("NB_APPEL"))).alias("NB_APPEL_3"),
                F.max(F.when(F.col("rank") == 4, F.col("NUMAPPLE"))).alias("ND_4"),
                F.max(F.when(F.col("rank") == 4, F.col("NB_APPEL"))).alias("NB_APPEL_4"),
                F.max(F.when(F.col("rank") == 5, F.col("NUMAPPLE"))).alias("ND_5"),
                F.max(F.when(F.col("rank") == 5, F.col("NB_APPEL"))).alias("NB_APPEL_5"),
                F.max(F.when(F.col("rank") == 6, F.col("NUMAPPLE"))).alias("ND_6"),
                F.max(F.when(F.col("rank") == 6, F.col("NB_APPEL"))).alias("NB_APPEL_6"),
                F.max(F.when(F.col("rank") == 7, F.col("NUMAPPLE"))).alias("ND_7"),
                F.max(F.when(F.col("rank") == 7, F.col("NB_APPEL"))).alias("NB_APPEL_7"),
                F.max(F.when(F.col("rank") == 8, F.col("NUMAPPLE"))).alias("ND_8"),
                F.max(F.when(F.col("rank") == 8, F.col("NB_APPEL"))).alias("NB_APPEL_8"),
                F.max(F.when(F.col("rank") == 9, F.col("NUMAPPLE"))).alias("ND_9"),
                F.max(F.when(F.col("rank") == 9, F.col("NB_APPEL"))).alias("NB_APPEL_9"),
                F.max(F.when(F.col("rank") == 10, F.col("NUMAPPLE"))).alias("ND_10"),
                F.max(F.when(F.col("rank") == 10, F.col("NB_APPEL"))).alias("NB_APPEL_10")
            )
            res = self.coalesce_if_needed(res)
            # Save the file
            self.process_and_save(res, output, bc, "MapR_CONSO_TOP10_ND")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e


    def MapR_CONSO_TOP10_DUREE(self, df, output, bc):
        try:
            # Apply caching to avoid recomputation
            df.cache()

            # Repartitioning the DataFrame for more efficient aggregation
            # df = df.repartition('ECHEANCE', 'CUSTCODE')

            # Aggregation
            result = df.groupBy("ND", "NUMAPPLE", "CUSTCODE", "ECHEANCE") \
                .agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")  # Total amount spent
            )

            # Ranking by total duration (to get top 10 durations)
            window_spec = Window.partitionBy("ND").orderBy(F.desc("TOTAL_DUREE"))
            ranked_result = result.withColumn("rank", F.row_number().over(window_spec))

            # Aggregating top 10 by duration
            res = ranked_result.groupBy("ECHEANCE", "CUSTCODE", "ND") \
                .agg(
                F.max(F.when(F.col("rank") == 1, F.col("NUMAPPLE"))).alias("ND_1"),
                F.max(F.when(F.col("rank") == 1, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_1"),
                F.max(F.when(F.col("rank") == 2, F.col("NUMAPPLE"))).alias("ND_2"),
                F.max(F.when(F.col("rank") == 2, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_2"),
                F.max(F.when(F.col("rank") == 3, F.col("NUMAPPLE"))).alias("ND_3"),
                F.max(F.when(F.col("rank") == 3, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_3"),
                F.max(F.when(F.col("rank") == 4, F.col("NUMAPPLE"))).alias("ND_4"),
                F.max(F.when(F.col("rank") == 4, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_4"),
                F.max(F.when(F.col("rank") == 5, F.col("NUMAPPLE"))).alias("ND_5"),
                F.max(F.when(F.col("rank") == 5, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_5"),
                F.max(F.when(F.col("rank") == 6, F.col("NUMAPPLE"))).alias("ND_6"),
                F.max(F.when(F.col("rank") == 6, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_6"),
                F.max(F.when(F.col("rank") == 7, F.col("NUMAPPLE"))).alias("ND_7"),
                F.max(F.when(F.col("rank") == 7, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_7"),
                F.max(F.when(F.col("rank") == 8, F.col("NUMAPPLE"))).alias("ND_8"),
                F.max(F.when(F.col("rank") == 8, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_8"),
                F.max(F.when(F.col("rank") == 9, F.col("NUMAPPLE"))).alias("ND_9"),
                F.max(F.when(F.col("rank") == 9, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_9"),
                F.max(F.when(F.col("rank") == 10, F.col("NUMAPPLE"))).alias("ND_10"),
                F.max(F.when(F.col("rank") == 10, F.col("TOTAL_DUREE"))).alias("DUREE_CUMUL_10")
            )
            res = self.coalesce_if_needed(res)
            # Save the file
            self.process_and_save(res, output, bc, "MapR_CONSO_TOP10_DUR")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e


    def FACTURE_ND(self, df, output, bc):
        try:
            # Apply caching to avoid recomputation
            df.cache()

            # Repartitioning the DataFrame for more efficient aggregation
            #df = df.repartition('ECHEANCE', 'CUSTCODE')

            # Aggregation
            res_df = df.groupBy("ECHEANCE", "CUSTCODE", "ND") \
                .agg(
                F.first("DT_ECHEANCE").alias("DATE_LIMITE"),
                F.first("MONTANTHT").alias("MONTANT_HT"),
                F.first("NUMFACTURE").alias("NUM_FACTURE")
            )

            res_df = self.coalesce_if_needed(res_df)
            # Save the file
            self.process_and_save(res_df, output, bc, "MapR_FACTURE_ND")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e


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
            bc = f"{int(parts[2]):02d}"

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



    # Check that df_list is not empty to avoid errors
    if df_list:
        # Use reduce to apply union to all DataFrames in the list
        df = reduce(DataFrame.union, df_list)
    # df.cache()
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
