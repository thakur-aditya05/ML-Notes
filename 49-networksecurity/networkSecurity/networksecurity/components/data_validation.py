from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging 
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH



# for the data drift we will use scipy library 
# this will basically check two sample of the data to find out weather there us is a data drift or not 
from scipy.stats import ks_2samp
import pandas as pd
import os,sys


# importing the readyaml file 
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file






# we know that input to this Datavalidation is dataIngestion Artifects and output is data_validation_config
# 
class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        
        try:
            # we are reading the data from data ingestion artifacts 
            self.data_ingestion_artifact=data_ingestion_artifact
            
            self.data_validation_config=data_validation_config
            # lest make a function to read yaml file inside utils 
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)



# lets make a function to read rthe data from the file path
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            # reading the data from csv file
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)


# let make a function to validate the number of columns 
# outcome will be true or false
    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            # lets check the number of columns
            # _schema_config ==>entire schema file present over here 
            number_of_columns=len(self._schema_config)
            
            logging.info(f"Required number of columns:{number_of_columns}")
            logging.info(f"Data frame has columns:{len(dataframe.columns)}")
            # checking the number of columns 
            # if number of columns are equal return true else false
            if len(dataframe.columns)==number_of_columns:
                # validation number of column are same 
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)


# lets make a function to detect the data drift 
# where current_df -> test dataframe
# base_df -> referance dataframe -> train dataframe
# threshold -> p value threshold
    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            status=True
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                # is sample ditribution is same or not
                is_same_dist=ks_2samp(d1,d2)
                
                if threshold<=is_same_dist.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=False
                
                
                # if drift was found we will add that to the report
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                    
                    }})
                
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            #Create directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report)

        except Exception as e:
            raise NetworkSecurityException(e,sys)


# return type is dataValidation Artifact
# initialise test and train file path from data ingestion component 
    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            ## read the data from train and test
            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)
            
            ## validate number of columns

            # for train dataframe
            error_message=""
            status=self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                error_message=f"Train dataframe does not contain all columns.\n"
                
            
            # for test dataframe
            status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                error_message=f"Test dataframe does not contain all columns.\n"   


            ## lets check datadrift
            
            # lets create the finction to detect the data drift(let  detect_dataset_drift)
            status=self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)
            # if status is true then there should entire data set should go inside my valid train_file path 
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            # if folder present then it will not give any error
            os.makedirs(dir_path,exist_ok=True)

            # lets save the file to the valid train file path
            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True

            )
            # lets save the file to the valid test file path
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )
            # see we didnt use status variable because if any of the status is false
            # then error message will be there so no need to check the status variable in above way  
            
            
            # return type is "dataValidation Artifact" which is present in artifact_entity
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)



