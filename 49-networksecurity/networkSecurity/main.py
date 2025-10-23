from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig

from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.entity.config_entity import ModelTrainerConfig
 

import sys

if __name__=='__main__':
    try:
        
        
        # lets check weather data ingestion pipeline is working or not 
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
        data_ingestion=DataIngestion(dataingestionconfig)
        logging.info("Initiate the data ingestion")
        dataingestionartifact=data_ingestion.initiate_data_ingestion()
        logging.info("Data Initiation Completed")
        print(dataingestionartifact)
        
        
        
        
        
        # our 2nd compents 
        # data validation we required two inputes dataingestionartifact data_validation_config
        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        data_validation=DataValidation(dataingestionartifact,data_validation_config)
        logging.info("Initiate the data Validation")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("data Validation Completed")
        print(data_validation_artifact)
        
        
        
        # this is my 3rd components
        # data transformation we required two inputes data_validation_artifact ,data_transformation_config
        data_transformation_config=DataTransformationConfig(trainingpipelineconfig)
        logging.info("data Transformation started")
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        # to get data transformation artifact we just need to call the initiate_data_transformation method
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)  # is this my output of this data transformation
        logging.info("data Transformation completed")



        # now we are ready for the model trainer part 
        logging.info("Model Training sstared")
        model_trainer_config=ModelTrainerConfig(trainingpipelineconfig)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        # just call the initiate_model_trainer method to start model training 
        model_trainer_artifact=model_trainer.initiate_model_trainer()
        logging.info("Model Training artifact created")
        
# all industry standard we have followed in developing this entire projects 
# MLflow for model tracking is tool to handle the model management (wrt experiment tracking )
    except Exception as e:
           raise NetworkSecurityException(e,sys)
