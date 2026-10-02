import shutil
import time

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
        # Initialize Spark session
        self.spark = SparkSession.builder.appName("Efacture Application Upgrade").getOrCreate()

        self.conf = SparkConf()
        self.sqlContext = SQLContext(self.spark)

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

    def factuteSimple(self,root):
        RVND=dict()
        RVNDL=list()
        for fac in root.iter('factureSimple'):
            
            CUSTCODE=fac.find('infoClient').attrib['custCode']
            ECHEANCE=fac.find('infoFacture').find('dateDebut').text[5:7]+"/"+fac.find('infoFacture').find('dateDebut').text[0:4]
            TYPERAPP=fac.find('infoClient').find('customerCat').text
            NUMFACTURE=fac.find('infoFacture').attrib['numFacture']
            DT_ECHEANCE=fac.find('infoFacture').find('dateEcheance').text[8:10]+"/"+fac.find('infoFacture').find('dateEcheance').text[5:7]+"/"+fac.find('infoFacture').find('dateEcheance').text[0:4]
            ND=fac.find('infoAbonnement').find('msisdn').text
            ND = "RECAP" if not ND or ND.strip() == "" else "212" + ND.lstrip("+0") if not ND.lstrip("+0").startswith("212") else ND.lstrip("+0")
            MONTANTHT=fac.find('totauxFacture').find('montantHT').text
            INDICFACTUREDET = fac.find('infoAbonnement').find('indicFactureDet').text

            if fac.find('grpDetailCom') is not None :
                for det in fac.find('grpDetailCom').findall("detailCom"):
                    DEST=det.attrib['codeCatCom']
                    CATDEST=det.attrib['codeCatCom']
                    if(det.find('numAppele').text is not None):
                        NUMAPPLE=det.find('numAppele').text
                    else:
                        NUMAPPLE=np.nan
                    if(det.find('heureAppel').text is not None):
                        if det.find('heureAppel').text[0:2]=="23":
                            HAPPLE= "23h-00h"
                        else:
                            HAPPLE=det.find('heureAppel').text[0:2]+"h-"+str(int(det.find('heureAppel').text[0:2])+1)+"h"
                    else:
                        HAPPLE=np.nan
                    if(det.find('dureeAppel').text is not None):
                        DUREE=int(det.find('dureeAppel').text)
                    else:
                        DUREE=np.nan
                    if(det.find('montantHT').text is not None):
                        MONTANT=float(det.find( 'montantHT').text)
                    else:
                        MONTANT=np.nan
                    if(det.find('dateAppel').text is not None):
                        DATEAPPEL=det.find( 'dateAppel').text
                    else:
                        DATEAPPEL=np.nan
                    RVNDL.append({'ECHEANCE':ECHEANCE,'CUSTCODE':CUSTCODE,'ND':ND,'DUREE':DUREE,'MONTANT':MONTANT,'DEST':DEST,"CATDEST":CATDEST,'NUMAPPLE':NUMAPPLE,'HEUREAPPLE':HAPPLE,'DATEAPPEL':DATEAPPEL,"NUMFACTURE":NUMFACTURE,'TYPERAPP':TYPERAPP,'DT_ECHEANCE':DT_ECHEANCE,"MONTANTHT":MONTANTHT, 'INDICFLAG': INDICFACTUREDET})
            else:
                RVNDL.append({'ECHEANCE': ECHEANCE,'CUSTCODE': CUSTCODE,'ND':ND, 'DT_ECHEANCE': DT_ECHEANCE, 'MONTANTHT': MONTANTHT, 'NUMFACTURE': NUMFACTURE   })

        myJson = self.spark.sparkContext.parallelize(RVNDL)
        myDf = self.sqlContext.read.json(myJson,schema=self.schema)
        return myDf


    def factureCompose(self,root):
        RVND=dict()
        RVNDL=list()
        for fac in root.iter('factureComposee'):

            CUSTCODE=fac.find('infoClient').attrib['custCode']
            ECHEANCE=fac.find('infoFacture').find('dateDebut').text[5:7]+"/"+fac.find('infoFacture').find('dateDebut').text[0:4]
            TYPERAPP=fac.find('infoClient').find('customerCat').text
            NUMFACTURE=fac.find('infoFacture').attrib['numFacture']
            DT_ECHEANCE=fac.find('infoFacture').find('dateEcheance').text[8:10]+"/"+fac.find('infoFacture').find('dateEcheance').text[5:7]+"/"+fac.find('infoFacture').find('dateEcheance').text[0:4]
            MONTANTHT=fac.find('totauxFacture').find('montantHT').text

            for abon in fac.iter('abonnement'):
                ND=abon.find('infoAbonnement').find('msisdn').text
                ND = "RECAP" if not ND or ND.strip() == "" else "212" + ND.lstrip("+0") if not ND.lstrip("+0").startswith("212") else ND.lstrip("+0")
                INDICFACTUREDET = abon.find('infoAbonnement').find('indicFactureDet').text
                if abon.find('grpDetailCom') is not None :
                    for det in abon.find('grpDetailCom').findall("detailCom"):
                        ND=abon[0][0].text
                        DEST=det.attrib['codeCatCom']
                        CATDEST=det.attrib['codeCatCom']
                        if(det.find('numAppele').text is not None):
                            NUMAPPLE=det.find('numAppele').text
                        else:
                            NUMAPPLE=np.nan
                        if(det.find('heureAppel').text is not None):
                            if det.find('heureAppel').text[0:2]=="23":
                                HAPPLE="23h-00h"
                            else:
                                HAPPLE=det.find('heureAppel').text[0:2]+"h-"+str(int(det.find('heureAppel').text[0:2])+1)+"h"
                        else:
                            HAPPLE=np.nan

                        if(det.find('dureeAppel').text is not None):
                            DUREE=int(det.find('dureeAppel').text)
                        else:
                            DUREE=np.nan
                        if(det.find('montantHT').text is not None):
                            MONTANT=float(det.find( 'montantHT').text)
                        else:
                            MONTANT=np.nan
                        if(det.find('dateAppel').text is not None):
                            DATEAPPEL=det.find( 'dateAppel').text
                        else:
                            DATEAPPEL=np.nan
                        RVNDL.append({'ECHEANCE':ECHEANCE,'CUSTCODE':CUSTCODE,'ND':ND,'DUREE':DUREE,'MONTANT':MONTANT,'DEST':DEST,"CATDEST":CATDEST,'NUMAPPLE':NUMAPPLE,'HEUREAPPLE':HAPPLE,'DATEAPPEL':DATEAPPEL,"NUMFACTURE":NUMFACTURE,'TYPERAPP':TYPERAPP,'DT_ECHEANCE':DT_ECHEANCE,'MONTANTHT':MONTANTHT, 'INDICFLAG': INDICFACTUREDET})
                else:
                    RVNDL.append({'ECHEANCE': ECHEANCE,'CUSTCODE': CUSTCODE,'ND': ND,'DT_ECHEANCE': DT_ECHEANCE, 'MONTANTHT': MONTANTHT, 'NUMFACTURE': NUMFACTURE   })

        myJson = self.spark.sparkContext.parallelize(RVNDL)
        myDf = self.sqlContext.read.json(myJson,schema=self.schema)
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
            df1= self.factuteSimple(root)
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
            emptyRDD=spark.sparkContext.emptyRDD()
            return spark.createDataFrame(emptyRDD,self.schema)


    def MapR_CONSO_ND(self, df, output, bc):
        try:
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            # Perform aggregation to match the SQL logic exactly
            result = df.groupBy("ECHEANCE", "CUSTCODE", "ND").agg(
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


    def MapR_CONSO_DEST_JOUR(self, df, output, bc):
        try:
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")


            # Grouping and aggregation
            result = df.groupby("ECHEANCE", "CUSTCODE", df["DEST"].alias("DESTINATION"),F.date_format(df["DATEAPPEL"],"dd/MM/yyyy").alias("JOUR")).agg(
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


    def MapR_CONSO_TRANCHE_HOR(self, df, output, bc):
        try:
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")
            result = df.groupby("ECHEANCE", "CUSTCODE", df["HEUREAPPLE"].alias("TRANCHE_HORAIRE")).agg(
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


    def MapR_CONSO_DEST_ND_JOUR(self, df, output, bc):
        try:
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            result = df.groupby("ECHEANCE", "CUSTCODE", "ND", df["DEST"].alias("DESTINATION"), F.date_format(df["DATEAPPEL"],"dd/MM/yyyy").alias("JOUR")).agg(
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


    def MapR_CALL_DEST(self, df, output, bc):
        try:
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            result = df.groupby("ECHEANCE", "CUSTCODE", "ND", df["DEST"].alias("DESTINATION")).agg(
                F.count("ND").alias("NB_APPEL"),
                F.sum("DUREE").alias("TOTAL_DUREE"),
                F.round(F.sum("MONTANT"), 2).alias("TOTAL_MONTANT")
            )

            res = df.groupby("ND").agg(F.count("ND").alias("tot_nb"))
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



    def MapR_CONSO_TOP10_ND(self, df, output, bc):
        try:
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            # Filteration & Aggregation
            result = df.groupBy("ND", "NUMAPPLE", "CUSTCODE", "ECHEANCE") \
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


    def MapR_CONSO_TOP10_DUREE(self,df, output, bc):
        try:
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            # Filteration & Aggregation
            result = df.groupBy("ND", "NUMAPPLE", "CUSTCODE", "ECHEANCE") \
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
            today = date.today()
            JJMMAAAA = today.strftime("%d%m%Y")

            res_df = df.groupBy("ECHEANCE", "CUSTCODE", "ND") \
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
                file_path = file_path[:-3]+"XML"

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
