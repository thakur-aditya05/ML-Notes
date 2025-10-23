
# importing some packages
import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer



# importing my config entity
from networksecurity.entity.config_entity import(
    TrainingPipelineConfig,
    DataIngestionConfig,        # --->output is  DataIngestionArtifact,
    DataValidationConfig,       # --->output is  DataValidationArtifact,
    DataTransformationConfig,   # --->output is  DataTransformationArtifact,
    ModelTrainerConfig,         # --->output is  ModelTrainerArtifact,
)

# importing  artifact entity
from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)


from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME
from networksecurity.cloud.s3_syncer import S3Sync
from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR
import sys



# we are going to write everything of the main.py  training pipeline in the form of the modularity

class TrainingPipeline:
    def __init__(self):
        # 1stly we have to initialise  training pipeline config
        self.training_pipeline_config=TrainingPipelineConfig()
        
        self.s3_sync = S3Sync()
        

    # start data ingestion method  1st
    def start_data_ingestion(self):
        try:
            # 1slty we have to require data ingestion config 
            self.data_ingestion_config=DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Start data Ingestion")
            # 2ndly we have to initialize data ingestion class 
            data_ingestion=DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
            logging.info(f"Data Ingestion completed and artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    
    # 2nd to start data validation method
    def start_data_validation(self,data_ingestion_artifact:DataIngestionArtifact):
        try:
            # 1stly we have to initialize data validation config
            data_validation_config=DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            # 2ndly we have to initialize data ingestion class 
            data_validation=DataValidation(data_ingestion_artifact=data_ingestion_artifact,data_validation_config=data_validation_config)
            logging.info("Initiate the data Validation")
            # output will be data validation artifact
            data_validation_artifact=data_validation.initiate_data_validation()
            # returning the data validation artifact
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    # 3rd to start data transformation method 
    def start_data_transformation(self,data_validation_artifact:DataValidationArtifact):
        try:
            # 1stly we have to initialize data transformation config
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            # 2ndly we have to initialize data transformation class
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config)
            # output will be data transformation artifact
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            # 
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    # 4th to start model trainer method
    def start_model_trainer(self,data_transformation_artifact:DataTransformationArtifact)->ModelTrainerArtifact:
        try:
            # 1stly we have to initialize model trainer config
            self.model_trainer_config: ModelTrainerConfig = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            # 2ndly we have to initialize model trainer class
            model_trainer = ModelTrainer(
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=self.model_trainer_config,
            )
            # output will be model trainer artifact
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            # returning the model trainer artifact
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# ======================================this is code to deploy the artifact to s3 bucket=================================================
# this is the code to push the local artifact to the s3 bucket

    ## local artifact is going to s3 bucket    
    def sync_artifact_dir_to_s3(self):
        try:
            # this is my bucket url so upload artifact to this path in s3 bucket 
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            # to sync the folder to s3 bucket (this is the function present inside the cloud )
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.artifact_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
# this is the code to push the local final model to the s3 bucket
    ## local final model is going to s3 bucket 
    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.model_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
# ======================================this is code to deploy the artifact to s3 bucket=================================================
        
    
    
    

# finally we are going to run the pipeline  that we have created above (this file is same as main.py)
    def run_pipeline(self):
        try:
            # this is normal to just run the pipeline
            data_ingestion_artifact=self.start_data_ingestion()
            data_validation_artifact=self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact=self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact=self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            
            
# ======================================================== to push the artifact and model to s3 bucket =======================================================
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
# ========================================================  to push the artifact and model to s3 bucket ======================================================= 
            
            
            # we are going to return the model trainer artifact at the end
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    
