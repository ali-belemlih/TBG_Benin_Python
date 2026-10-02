import sys
import os
import numpy as np
import pandas as pd
import psutil
from pyspark.sql.functions import sum,count
from pyspark.sql.types import *
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
import xml.etree.ElementTree as ET
import pyspark as ps
from datetime import date
from pyspark.sql import Row
from dateutil.parser import parse
from pyspark.sql import SQLContext


conf = SparkConf().setAppName("Efacture Application").set("spark.ui.port", "18080")

spark = SparkSession \
    .builder \
    .appName("Python Spark SQL Entrant Sortant") \
    .getOrCreate()

sqlContext = SQLContext(spark)

#Function to extract all needed informations from xml

schema = StructType([
    StructField("ECHEANCE", StringType(), True),
    StructField("CUSTCODE", StringType(), True),
    StructField("ND", StringType(), True),
    StructField("DUREE", FloatType(), True),
    StructField("MONTANT", FloatType(), True),
    StructField("DEST",  StringType(),True),
    StructField("CATDEST",  StringType(),True),
    StructField("NUMAPPLE",  StringType(),True),
    StructField("HEUREAPPLE",  StringType(),True),
    StructField("DATEAPPEL",  StringType(),True),
    StructField("NUMFACTURE",  StringType(),True),
    StructField("TYPERAPP",  StringType(),True),
    StructField("DT_ECHEANCE",  StringType(),True),
    StructField("MONTANTHT",  StringType(),True),
    StructField("INDICFLAG", StringType(), True)
])

def factuteSimple(root):
    RVND=dict()
    RVNDL=list()
    for fac in root.iter('factureSimple'):
            if fac.find('grpDetailCom') is not None :
                    CUSTCODE=fac.find('infoClient').attrib['custCode']
                    ECHEANCE=fac.find('infoFacture').find('dateDebut').text[5:7]+"/"+fac.find('infoFacture').find('dateDebut').text[0:4]
                    TYPERAPP=fac.find('infoClient').find('customerCat').text
                    NUMFACTURE=fac.find('infoFacture').attrib['numFacture']
                    DT_ECHEANCE=fac.find('infoFacture').find('dateEcheance').text[8:10]+"/"+fac.find('infoFacture').find('dateEcheance').text[5:7]+"/"+fac.find('infoFacture').find('dateEcheance').text[0:4]
                    ND=fac.find('infoAbonnement').find('msisdn').text
                    MONTANTHT=fac.find('totauxFacture').find('montantHT').text
                    INDICFACTUREDET = fac.find('infoAbonnement').find('indicFactureDet').text
                    
                    for det in fac.find('grpDetailCom').findall("detailCom"):
                        DEST=det.attrib['typeCom']
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
                       # CATDEST=np.nan
                       # DEST=np.nan
                       #MONTANT=np.nan
                       # DUREE=np.nan
                        #DATEAPPEL=np.nan
                        #HAPPLE=np.nan
                        #NUMAPPLE=np.nan
                        #RVNDL.append({'ECHEANCE':ECHEANCE,'CUSTCODE':CUSTCODE,'ND':ND,'DUREE':DUREE,'MONTANT':MONTANT,'DEST':DEST,"CATDEST":CATDEST,'NUMAPPLE':NUMAPPLE,"HEUREAPPLE":HAPPLE,'DATEAPPEL':DATEAPPEL,"NUMFACTURE":NUMFACTURE,'TYPERAPP':TYPERAPP,'DT_ECHEANCE':DT_ECHEANCE})
                        CUSTCODE=fac.find('infoClient').attrib['custCode']
                        ECHEANCE=fac.find('infoFacture').find('dateDebut').text[5:7]+"/"+fac.find('infoFacture').find('dateDebut').text[0:4]
                        DT_ECHEANCE=fac.find('infoFacture').find('dateEcheance').text[8:10]+"/"+fac.find('infoFacture').find('dateEcheance').text[5:7]+"/"+fac.find('infoFacture').find('dateEcheance').text[0:4]
                        MONTANTHT = fac.find('totauxFacture').find('montantHT').text
                        NUMFACTURE=fac.find('infoFacture').attrib['numFacture']
                        RVNDL.append({'ECHEANCE': ECHEANCE,'CUSTCODE': CUSTCODE,'DT_ECHEANCE': DT_ECHEANCE, 'MONTANTHT': MONTANTHT, 'NUMFACTURE': NUMFACTURE   })

            


    myJson = spark.sparkContext.parallelize(RVNDL)
    myDf = sqlContext.read.json(myJson,schema=schema)
    return myDf


# In[14]:


def factureCompose(root):
    RVND=dict()
    RVNDL=list()
    for fac in root.iter('factureComposee'):
            for abon in fac.iter('abonnement'):
                ND=abon.find('infoAbonnement').find('msisdn').text
                INDICFACTUREDET = abon.find('infoAbonnement').find('indicFactureDet').text
                if abon.find('grpDetailCom') is not None :
                    CUSTCODE=fac.find('infoClient').attrib['custCode']
                    ECHEANCE=fac.find('infoFacture').find('dateDebut').text[5:7]+"/"+fac.find('infoFacture').find('dateDebut').text[0:4]
                    TYPERAPP=fac.find('infoClient').find('customerCat').text
                    NUMFACTURE=fac.find('infoFacture').attrib['numFacture']
                    DT_ECHEANCE=fac.find('infoFacture').find('dateEcheance').text[8:10]+"/"+fac.find('infoFacture').find('dateEcheance').text[5:7]+"/"+fac.find('infoFacture').find('dateEcheance').text[0:4]
                    MONTANTHT=fac.find('totauxFacture').find('montantHT').text
                    for det in abon.find('grpDetailCom').findall("detailCom"):
                        ND=abon[0][0].text
                        DEST=det.attrib['typeCom']
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
                        #CATDEST=np.nan
                        #DEST=np.nan
                        #MONTANT=np.nan
                        #DUREE=np.nan
                        #DATEAPPEL=np.nan
                        #HAPPLE=np.nan
                        #NUMAPPLE=np.nan
                        #RVNDL.append({'ECHEANCE':ECHEANCE,'CUSTCODE':CUSTCODE,'ND':ND,'DUREE':DUREE,'MONTANT':MONTANT,'DEST':DEST,"CATDEST":CATDEST,'NUMAPPLE':NUMAPPLE,"HEUREAPPLE":HAPPLE,'DATEAPPEL':DATEAPPEL,"NUMFACTURE":NUMFACTURE,'TYPERAPP':TYPERAPP,'DT_ECHEANCE':DT_ECHEANCE})
                        CUSTCODE=fac.find('infoClient').attrib['custCode']
                        ECHEANCE=fac.find('infoFacture').find('dateDebut').text[5:7]+"/"+fac.find('infoFacture').find('dateDebut').text[0:4]
                        DT_ECHEANCE=fac.find('infoFacture').find('dateEcheance').text[8:10]+"/"+fac.find('infoFacture').find('dateEcheance').text[5:7]+"/"+fac.find('infoFacture').find('dateEcheance').text[0:4]
                        MONTANTHT=fac.find('totauxFacture').find('montantHT').text
                        NUMFACTURE=fac.find('infoFacture').attrib['numFacture']
                        RVNDL.append({'ECHEANCE': ECHEANCE,'CUSTCODE': CUSTCODE,'ND': ND,'DT_ECHEANCE': DT_ECHEANCE, 'MONTANTHT': MONTANTHT, 'NUMFACTURE': NUMFACTURE   })

    myJson = spark.sparkContext.parallelize(RVNDL)
    myDf = sqlContext.read.json(myJson,schema=schema)
    return myDf


def log_memory_and_cpu_usage():
        # Retrieve the current virtual memory usage statistics
    memory_info = psutil.virtual_memory()
    cpu_usage = psutil.cpu_percent(interval=1) #In Seconds

    print(f"Memory Usage: {memory_info.percent}%")
    print(f"Available Memory: {memory_info.available / (1024 * 1024):.2f} MB")
    print(f"Total Memory: {memory_info.total / (1024 * 1024):.2f} MB")
    print(f"CPU Usage: {cpu_usage}%")

# parse the xml file
import shutil
def extractAll(path):

  try:
    tree = ET.parse(path)
    root = tree.getroot()
    df1=factuteSimple(root)
    df2=factureCompose(root)
    
    if(df2.count()==0):
        return df1
    elif(df1.count()==0):
        return df2
    else:
        #return pd.concat([df1,df2],ignore_index=True)<
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
            return spark.createDataFrame(emptyRDD,schema)

#MapR_CONSO_ND_MMAAAA_JJMMAAAA

def MapR_CONSO_ND(df,output,bc):
    MMAAAA=df.select("ECHEANCE").first()[0].replace("/","")
    today = date.today()
    JJMMAAAA=today.strftime("%d%m%Y")
    df.createOrReplaceTempView("MapR_CONSO_ND")
    result=spark.sql(""" select ECHEANCE,CUSTCODE,ND,count(ND) as NB_APPEL ,sum(DUREE) as TOTAL_DUREE, ROUND(SUM(MONTANT), 2) as TOTAL_MONTANT  from MapR_CONSO_ND where DEST in("Nat","Int","Spec") group by ND,CUSTCODE,ECHEANCE """)
    df=result.toPandas()

    grouped_df = df.groupby("ECHEANCE")
    for datetag, group in grouped_df:
        echeance = group["ECHEANCE"].iloc[0]
        prefix_path = output+"/"+echeance.replace("/","")
        isExist = os.path.exists(prefix_path)

        if not isExist:
            os.mkdir(prefix_path)

        filename=prefix_path+"/"+"MapR_CONSO_ND_"+datetag.replace("/","")+"_"+JJMMAAAA+"_"+bc+".txt"
        group.to_csv(filename, sep=";", index=False)
    

#MapR_CONSO_DEST_JOUR
def MapR_CONSO_DEST_JOUR(df,output,bc):
    MMAAAA=df.select("ECHEANCE").first()[0].replace("/","")
    today = date.today()
    JJMMAAAA=today.strftime("%d%m%Y")
    df.createOrReplaceTempView("MapR_CONSO_DEST_JOUR")
    result=spark.sql(""" select ECHEANCE,CUSTCODE,DEST as DESTINATION,DATEAPPEL as JOUR ,count(ND) as NB_APPEL ,sum(DUREE) as TOTAL_DUREE, ROUND(SUM(MONTANT), 2) as TOTAL_MONTANT  from MapR_CONSO_DEST_JOUR  where DEST in ("Nat","Int","Spec") group by CUSTCODE,ECHEANCE,DESTINATION,JOUR """)
    df=result.toPandas()
    
    grouped_df = df.groupby("ECHEANCE")
    for datetag, group in grouped_df:
        echeance = group["ECHEANCE"].iloc[0]
        prefix_path = output+"/"+echeance.replace("/","")
        isExist = os.path.exists(prefix_path)

        if not isExist:
            os.mkdir(prefix_path)

        filename=prefix_path+"/"+"MapR_CONSO_DEST_JOUR_"+datetag.replace("/","")+"_"+JJMMAAAA+"_"+bc+".txt"
        group.to_csv(filename, sep=";", index=False)


#MapR_CONSO_TRANCHE_HOR_MMAAAA_JJMMAAAA
def MapR_CONSO_TRANCHE_HOR(df,output,bc):
    MMAAAA=df.select("ECHEANCE").first()[0].replace("/","")
    today = date.today()
    JJMMAAAA=today.strftime("%d%m%Y")
    df.createOrReplaceTempView("MapR_CONSO_TRANCHE_HOR")
    result=spark.sql(""" select ECHEANCE,CUSTCODE,HEUREAPPLE as TRANCHE_HORAIRE,count(ND) as NB_APPEL ,sum(DUREE) as TOTAL_DUREE, ROUND(SUM(MONTANT), 2) as TOTAL_MONTANT  from MapR_CONSO_TRANCHE_HOR  where DEST in ("Nat","Int","Spec") group by CUSTCODE,ECHEANCE,TRANCHE_HORAIRE """)
    df=result.toPandas()

    grouped_df = df.groupby("ECHEANCE")
    for datetag, group in grouped_df:
        echeance = group["ECHEANCE"].iloc[0]
        prefix_path = output+"/"+echeance.replace("/","")
        isExist = os.path.exists(prefix_path)

        if not isExist:
            os.mkdir(prefix_path)

        filename=prefix_path+"/"+"MapR_CONSO_TRANCHE_HOR_"+datetag.replace("/","")+"_"+JJMMAAAA+"_"+bc+".txt"
        group.to_csv(filename, sep=";", index=False)


#MapR_CONSO_DEST_ND_JOUR_MMAAAA_JJMMAAAA
def MapR_CONSO_DEST_ND_JOUR(df,output,bc):
    MMAAAA=df.select("ECHEANCE").first()[0].replace("/","")
    today = date.today()
    JJMMAAAA=today.strftime("%d%m%Y")
    df.createOrReplaceTempView("MapR_CONSO_DEST_ND_JOUR")
    result=spark.sql(""" select ECHEANCE,CUSTCODE,ND,DEST as DESTINATION,DATEAPPEL as JOUR ,count(ND) as NB_APPEL ,sum(DUREE) as TOTAL_DUREE, ROUND(SUM(MONTANT), 2) as TOTAL_MONTANT  from MapR_CONSO_TRANCHE_HOR  where DEST in ("Nat","Int","Spec") group by ND,CUSTCODE,ECHEANCE,DESTINATION,JOUR """)
    df=result.toPandas()
    grouped_df = df.groupby("ECHEANCE")
    for datetag, group in grouped_df:
        echeance = group["ECHEANCE"].iloc[0]
        prefix_path = output+"/"+echeance.replace("/","")
        isExist = os.path.exists(prefix_path)

        if not isExist:
            os.mkdir(prefix_path)

        filename=prefix_path+"/"+"MapR_CONSO_ND_DEST_JOUR_"+datetag.replace("/","")+"_"+JJMMAAAA+"_"+bc+".txt"
        group.to_csv(filename, sep=";", index=False)


#Appels sortants par destination

def MapR_CALL_DEST(df,output,bc):
    MMAAAA=df.select("ECHEANCE").first()[0].replace("/","")
    today = date.today()
    JJMMAAAA=today.strftime("%d%m%Y")
    df.createOrReplaceTempView("MapR_CALL_DEST")
    result=spark.sql(""" select ECHEANCE,CUSTCODE,ND,DEST as DESTINATION,count(ND) as NB_APPEL ,sum(DUREE) as TOTAL_DUREE, ROUND(SUM(MONTANT), 2) as TOTAL_MONTANT from MapR_CALL_DEST where DEST in ("Nat","Int","Spec") group by ND,DESTINATION,CUSTCODE,ECHEANCE """)
    result.createOrReplaceTempView("T1")
    res=spark.sql(""" select ND,count(ND) as tot_nb from MapR_CALL_DEST where DEST in ("Nat","Int","Spec") group by ND""")
    res.createOrReplaceTempView("T2")
    f_res=spark.sql(""" select t1.* ,(t1.NB_APPEL/t2.tot_nb)*100 as POURCENTAGE from  T1 t1,T2 t2 where t1.ND=t2.ND """)
    df=f_res.toPandas()

    grouped_df = df.groupby("ECHEANCE")
    for datetag, group in grouped_df:
        echeance = group["ECHEANCE"].iloc[0]
        prefix_path = output+"/"+echeance.replace("/","")
        isExist = os.path.exists(prefix_path)

        if not isExist:
            os.mkdir(prefix_path)

        filename=prefix_path+"/"+"MapR_CONSO_ND_DEST_"+datetag.replace("/","")+"_"+JJMMAAAA+"_"+bc+".txt"
        group.to_csv(filename, sep=";", index=False)


#MapR_CONSO_TOP10_ND

def MapR_CONSO_TOP10_ND(df,output,bc):
    MMAAAA=df.select("ECHEANCE").first()[0].replace("/","")
    today = date.today()
    JJMMAAAA=today.strftime("%d%m%Y")
    df.createOrReplaceTempView("MapR_CONSO_TOP10_ND")
    result=spark.sql(""" select ECHEANCE,CUSTCODE,ND,NUMAPPLE,count(ND) as NB_APPEL ,sum(DUREE) as TOTAL_DUREE, ROUND(SUM(MONTANT), 2) as TOTAL_MONTANT from MapR_CONSO_TOP10_ND where DEST in ("Nat","Int","Spec") group by ND,NUMAPPLE,CUSTCODE,ECHEANCE""")
    result.createOrReplaceTempView("MapR_CONSO_TOP10_ND_S")
    spark.sql(""" select * from (select CUSTCODE,ECHEANCE,ND,NUMAPPLE,NB_APPEL, row_number() over (partition by ND order by NB_APPEL desc) as rank from MapR_CONSO_TOP10_ND_S) ranks  where rank<=10 """).createOrReplaceTempView("MapR_CONSO_TOP10_ND_RES")
    spark.sql("""select ECHEANCE,CUSTCODE,ND,NUMAPPLE as ND_1,NB_APPEL as NB_APPEL_1 from MapR_CONSO_TOP10_ND_RES where rank=1""").createOrReplaceTempView("t1")
    spark.sql("""select ND,NUMAPPLE as ND_2,NB_APPEL as NB_APPEL_2 from MapR_CONSO_TOP10_ND_RES where rank=2""").createOrReplaceTempView("t2")
    spark.sql("""select ND,NUMAPPLE as ND_3,NB_APPEL as NB_APPEL_3 from MapR_CONSO_TOP10_ND_RES where rank=3""").createOrReplaceTempView("t3")
    spark.sql("""select ND,NUMAPPLE as ND_4,NB_APPEL as NB_APPEL_4 from MapR_CONSO_TOP10_ND_RES where rank=4""").createOrReplaceTempView("t4")
    spark.sql("""select ND,NUMAPPLE as ND_5,NB_APPEL as NB_APPEL_5 from MapR_CONSO_TOP10_ND_RES where rank=5""").createOrReplaceTempView("t5")
    spark.sql("""select ND,NUMAPPLE as ND_6,NB_APPEL as NB_APPEL_6 from MapR_CONSO_TOP10_ND_RES where rank=6""").createOrReplaceTempView("t6")
    spark.sql("""select ND,NUMAPPLE as ND_7,NB_APPEL as NB_APPEL_7 from MapR_CONSO_TOP10_ND_RES where rank= 7 """).createOrReplaceTempView("t7")
    spark.sql("""select ND,NUMAPPLE as ND_8,NB_APPEL as NB_APPEL_8 from MapR_CONSO_TOP10_ND_RES where rank=8""").createOrReplaceTempView("t8")
    spark.sql("""select ND,NUMAPPLE as ND_9,NB_APPEL as NB_APPEL_9 from MapR_CONSO_TOP10_ND_RES where rank=9""").createOrReplaceTempView("t9")
    spark.sql("""select ND,NUMAPPLE as ND_10,NB_APPEL as NB_APPEL_10 from MapR_CONSO_TOP10_ND_RES where rank=10""").createOrReplaceTempView("t10")
    res=spark.sql(""" select t1.*,t2.ND_2,t2.NB_APPEL_2,t3.ND_3,t3.NB_APPEL_3,t4.ND_4,t4. NB_APPEL_4,t5.ND_5,t5.NB_APPEL_5,t6.ND_6,t6.NB_APPEL_6,t7.ND_7,t7.NB_APPEL_7,t8.ND_8,t8.NB_APPEL_8,t9.ND_9,t9.NB_APPEL_9,t10.ND_10,t10.NB_APPEL_10  from t1,t2,t3,t4,t5,t6,t7,t8,t9,t10 where t1.ND=t2.ND and t2.ND=t3.ND and t3.ND=t4.ND and t4.ND=t5.ND and t5.ND=t6.ND and t6.ND=t7.ND and t7.ND=t8.ND and t8.ND=t9.ND and t9.ND=t10.ND """)
    df=res.toPandas()
    grouped_df = df.groupby("ECHEANCE")
    for datetag, group in grouped_df:
        echeance = group["ECHEANCE"].iloc[0]
        prefix_path = output+"/"+echeance.replace("/","")
        isExist = os.path.exists(prefix_path)

        if not isExist:
            os.mkdir(prefix_path)

        filename=prefix_path+"/"+"MapR_CONSO_TOP10_ND_"+datetag.replace("/","")+"_"+JJMMAAAA+"_"+bc+".txt"
        group.to_csv(filename, sep=";", index=False)


# # Liste des top 10 durées d'appel cumulées les plus longues

# In[69]:


def MapR_CONSO_TOP10_DUREE(df,output,bc):
    MMAAAA=df.select("ECHEANCE").first()[0].replace("/","")
    today = date.today()
    JJMMAAAA=today.strftime("%d%m%Y")
    df.createOrReplaceTempView("MapR_CONSO_TOP10_DUREE")
    result=spark.sql(""" select ECHEANCE,CUSTCODE,ND,NUMAPPLE,count(ND) as NB_APPEL ,sum(DUREE) as TOTAL_DUREE, ROUND(SUM(MONTANT), 2) as TOTAL_MONTANT from MapR_CONSO_TOP10_DUREE where DEST in ("Nat","Int","Spec") group by ND,NUMAPPLE,CUSTCODE,ECHEANCE""")
    result.createOrReplaceTempView("MapR_CONSO_TOP10_DUREE_S")
    spark.sql(""" select * from (select CUSTCODE,ECHEANCE,ND,NUMAPPLE,TOTAL_DUREE, row_number() over (partition by ND order by TOTAL_DUREE desc) as rank from MapR_CONSO_TOP10_ND_S) ranks  where rank<=10 """).createOrReplaceTempView("MapR_CONSO_TOP10_ND_RES")
    spark.sql("""select ECHEANCE,CUSTCODE,ND,NUMAPPLE as ND_1,TOTAL_DUREE  as DUREE_CUMUL_1 from MapR_CONSO_TOP10_ND_RES where rank=1""").createOrReplaceTempView("t1")
    spark.sql("""select ND,NUMAPPLE as ND_2, TOTAL_DUREE  as DUREE_CUMUL_2 from MapR_CONSO_TOP10_ND_RES where rank=2""").createOrReplaceTempView("t2")
    spark.sql("""select ND,NUMAPPLE as ND_3,TOTAL_DUREE as DUREE_CUMUL_3 from MapR_CONSO_TOP10_ND_RES where rank=3""").createOrReplaceTempView("t3")
    spark.sql("""select ND,NUMAPPLE as ND_4,TOTAL_DUREE as DUREE_CUMUL_4 from MapR_CONSO_TOP10_ND_RES where rank=4""").createOrReplaceTempView("t4")
    spark.sql("""select ND,NUMAPPLE as ND_5,TOTAL_DUREE as DUREE_CUMUL_5 from MapR_CONSO_TOP10_ND_RES where rank=5""").createOrReplaceTempView("t5")
    spark.sql("""select ND,NUMAPPLE as ND_6,TOTAL_DUREE as DUREE_CUMUL_6 from MapR_CONSO_TOP10_ND_RES where rank=6""").createOrReplaceTempView("t6")
    spark.sql("""select ND,NUMAPPLE as ND_7,TOTAL_DUREE as DUREE_CUMUL_7 from MapR_CONSO_TOP10_ND_RES where rank= 7 """).createOrReplaceTempView("t7")
    spark.sql("""select ND,NUMAPPLE as ND_8,TOTAL_DUREE as DUREE_CUMUL_8 from MapR_CONSO_TOP10_ND_RES where rank=8""").createOrReplaceTempView("t8")
    spark.sql("""select ND,NUMAPPLE as ND_9,TOTAL_DUREE as DUREE_CUMUL_9 from MapR_CONSO_TOP10_ND_RES where rank=9""").createOrReplaceTempView("t9")
    spark.sql("""select ND,NUMAPPLE as ND_10,TOTAL_DUREE as DUREE_CUMUL_10 from MapR_CONSO_TOP10_ND_RES where rank=10""").createOrReplaceTempView("t10")
    res=spark.sql(""" select t1.*,t2.ND_2,t2.DUREE_CUMUL_2,t3.ND_3,t3.DUREE_CUMUL_3,t4.ND_4,t4. DUREE_CUMUL_4,t5.ND_5,t5.DUREE_CUMUL_5,t6.ND_6,t6.DUREE_CUMUL_6,t7.ND_7,t7.DUREE_CUMUL_7,t8.ND_8,t8.DUREE_CUMUL_8,t9.ND_9,t9.DUREE_CUMUL_9,t10.ND_10,t10.DUREE_CUMUL_10  from t1,t2,t3,t4,t5,t6,t7,t8,t9,t10 where t1.ND=t2.ND and t2.ND=t3.ND and t3.ND=t4.ND and t4.ND=t5.ND and t5.ND=t6.ND and t6.ND=t7.ND and t7.ND=t8.ND and t8.ND=t9.ND and t9.ND=t10.ND """)
    df=res.toPandas()
    grouped_df = df.groupby("ECHEANCE")
    for datetag, group in grouped_df:
        echeance = group["ECHEANCE"].iloc[0]
        prefix_path = output+"/"+echeance.replace("/","")
        isExist = os.path.exists(prefix_path)

        if not isExist:
            os.mkdir(prefix_path)

        filename=prefix_path+"/"+"MapR_CONSO_TOP10_DUR_"+datetag.replace("/","")+"_"+JJMMAAAA+"_"+bc+".txt"
        group.to_csv(filename, sep=";", index=False)

#MapR_FACTURE_ND_MMAAAA_JJMMAAAA

def FACTURE_ND(df,output,bc):
    MMAAAA=df.select("ECHEANCE").first()[0].replace("/","")
    today = date.today()
    JJMMAAAA=today.strftime("%d%m%Y")
    df.createOrReplaceTempView("FACTURE_ND")
    res=spark.sql(""" select ECHEANCE,CUSTCODE,"RECAP" as ND,DT_ECHEANCE as DATE_LIMITE, MONTANTHT as MONTANT_HT ,NUMFACTURE as NUM_FACTURE from FACTURE_ND group by ECHEANCE,CUSTCODE,ND,DATE_LIMITE,NUM_FACTURE,MONTANT_HT """)
    df = res.toPandas().drop_duplicates()

    grouped_df = df.groupby("ECHEANCE")
    for datetag, group in grouped_df:
        echeance = group["ECHEANCE"].iloc[0]
        prefix_path = output+"/"+echeance.replace("/","")
        isExist = os.path.exists(prefix_path)

        if not isExist:
            os.mkdir(prefix_path)

        filename=prefix_path+"/"+"FACTURE_ND_"+datetag.replace("/","")+"_"+JJMMAAAA+"_"+bc+".txt"
        group.to_csv(filename, sep=";", index=False)


def is_date(string, fuzzy=True):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

#The main function
import time
import shutil
import datetime
import os
import gzip

if __name__ == "__main__":

    # the path to the sources files
    directory = os.getcwd()

    # set the path to the output folder's files
    parent = os.path.abspath(os.path.join(directory, os.pardir))
    isExist = os.path.exists(parent + "/output_files")
    if not isExist:
        os.mkdir(parent + "/output_files")
    output = parent + "/output_files"

    start = time.time()
    emptyRDD = spark.sparkContext.emptyRDD()
    df = spark.createDataFrame(emptyRDD, schema)

    # Get yesterday's date
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')

    directory = directory+"/Input/"
    print("Before processing files:")
    log_memory_and_cpu_usage()
    for filename in os.listdir(directory):
        print(filename)
        if filename.startswith("BGH"):
            print("Start Traitement")
            parts = filename.split(".")
            bc=parts[2]
            f = os.path.join(directory, filename)
            if filename.endswith(".XML.gz"):
                # Décompression du fichier .XML.gz
                with gzip.open(f, 'rb') as gz_file:
                    content = gz_file.read()
                    with open(f[:-3], 'wb') as xml_file:
                        xml_file.write(content)
                os.remove(f)
                f = f[:-3]
                if extractAll(f).count() > 0:
                    df = df.union(extractAll(f[:-3]+"XML"))
                    print("Le fichier " + filename + " a été analysé avec succès et sera déplacé vers le dossier 'Parsed_files'")

            if filename.endswith(".XML") :
                print(extractAll(f).count())
                print("Le traitement sur le fichier XML directement")
                # Le traitement sur le fichier XML directement
                if extractAll(f).count() > 0:
                    df = df.union(extractAll(f))
                    print("Le fichier " + filename + " a été analysé avec succès et sera déplacé vers le dossier 'Parsed_files'")
            # Déplacer le fichier analysé vers le dossier "Parsed_files"
            #shutil.move(f, os.path.join(parent, "Parsed_files"))

    # all below functions return a csv file
    if df.count() > 0:
        FACTURE_ND(df, output,bc)
        df = df.filter(df["INDICFLAG"] != 'N')
        if df.count() != 0:
            MapR_CONSO_ND(df, output,bc)
            MapR_CONSO_DEST_JOUR(df, output,bc)
            MapR_CONSO_TRANCHE_HOR(df, output,bc)
            MapR_CONSO_DEST_ND_JOUR(df, output,bc)
            MapR_CALL_DEST(df, output,bc)
            MapR_CONSO_TOP10_ND(df, output,bc)
            MapR_CONSO_TOP10_DUREE(df, output,bc)

    print("After processing files:")
    log_memory_and_cpu_usage()

    elapsed_time_fl = (time.time() - start)
    print(elapsed_time_fl)