

# 1
# import the networksecurity exception and logging module
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


## lets call  configuration of the Data Ingestion Config

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import numpy as np
import pandas as pd
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
load_dotenv()


# reading from mongo db database


# getting the url of the mongodb database from the env file 
MONGO_DB_URL=os.getenv("MONGO_DB_URL")

# lets start reading the data from the mongodb database
class DataIngestion:
    # if we want to read the data from the mongodb database we need to know all the configuration details from DataIngestionConfig class
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)




# 2 methods are created
# from mongoDb we need to export the data into feature store 
    def export_collection_as_dataframe(self):
        """
        Read data from mongodb
        """
        """
            this particular function is then called in the initiate_data_ingestion function
            we will read the data from the mongodb database and convert that data into dataframe
        """
        try:
            # read of data base from the config entity
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            # mmongoclient instance creation
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]
            
            # converting the data into dataframe
            df=pd.DataFrame(list(collection.find()))
            
            # by deadult we get the _id column in the dataframe so we need to drop that column
            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"],axis=1)
            
            # replacing the na values with np.nan
            df.replace({"na":np.nan},inplace=True)
            return df
        
        except Exception as e:
            raise NetworkSecurityException

# 3rd method 
# passing the dataFarme to the feature store
    def export_data_into_feature_store(self,dataframe: pd.DataFrame):
        try:
            # features store file path 
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            #creating folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            # converting the dataframe to csv file, which will be storing in features store file path 
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)



# 4th mehtod 
# train text split is available in sklearn library
    def split_data_as_train_test(self,dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train test split on the dataframe")

            logging.info(
                "Exited split_data_as_train_test method of Data_Ingestion class"
            )
            
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            
            os.makedirs(dir_path, exist_ok=True)
            
            logging.info(f"Exporting train and test file path.")
            
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logging.info(f"Exported train and test file path.")

            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
# 1st class is created to ingests the data
# we need to initiate the data ingestion CONFIG already we have mongo db url 
    def initiate_data_ingestion(self):
        try:
            
            # from here we get data from mongodb and convert it into dataframe
            # 1st step of reading the data from mongodb data is complleted 
            dataframe=self.export_collection_as_dataframe()
            
            # we need to export this data into feature store
            # that is inside data ingestion folder we have somthing called feature store  having the csv file and have the entire data 
            # 
            dataframe=self.export_data_into_feature_store(dataframe)
            
            # this is just train test split 
            self.split_data_as_train_test(dataframe)
            
            
            
            # 
            dataingestionartifact=DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
                                                        test_file_path=self.data_ingestion_config.testing_file_path)
            return dataingestionartifact

        except Exception as e:
            raise NetworkSecurityException