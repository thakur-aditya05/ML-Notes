import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()   # to call environment variables from .env file


# to check if environment variable is loading or not
MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)


import certifi
# provides a set of roots certificate 
# it retrive the the part to the bundle of ca certificates ptovided by certufy and store it in
# done for ssl and tls connection
# server are connecting to hhas  trusted certificates ennsured 
ca=certifi.where()






# our source is in Network_Data=>phisingData.csv 
import pandas as pd
import numpy as np
import pymongo
# logging and exception ko use krne k liye
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


# Etl pipeline which will be responsible for doing all those things 
class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def csv_to_json_convertor(self,file_path):
        try:
            # reding the csv file py giving th path
            data=pd.read_csv(file_path)
            # reseting the index of the dataframe
            data.reset_index(drop=True,inplace=True)
            # converting the data into json format of key value pair 
            records=list(json.loads(data.T.to_json()).values()) 
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
        
    # inserting the data into mongodb database
    # database and collection name will be passed by the user 
    def insert_data_mongodb(self,records,database,collection):
        try:
            # making the instance variable
            self.database=database
            self.collection=collection
            self.records=records

            # connecting to mongodb database
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            # in this mongo client what database we are using
            self.database = self.mongo_client[self.database]
            # what collection we are using iin this database
            self.collection=self.database[self.collection]
            # inserting the data into the collection
            self.collection.insert_many(self.records)
            # how many records are inserted
            return(len(self.records))
        except Exception as e:
            raise NetworkSecurityException(e,sys)




# now we will call the above class and its methods    
# lets start execution of the code
if __name__=='__main__':
    FILE_PATH="Network_Data\phisingData.csv"
    DATABASE="KRISHAI"
    Collection="NetworkData"
    networkobj=NetworkDataExtract()
    records=networkobj.csv_to_json_convertor(file_path=FILE_PATH)
    print(records)
    # passing the recorda to the insert methodN
    no_of_records=networkobj.insert_data_mongodb(records,DATABASE,Collection)
    
    print(no_of_records)
        


