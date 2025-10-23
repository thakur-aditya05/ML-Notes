
# step 4 of data transformation part 


import sys
import os
import numpy as np
import pandas as pd

# knn imputer is used to fill the missing values
from sklearn.impute import KNNImputer     
from sklearn.pipeline import Pipeline


# i need to drop target column from the data set for this we should import target column from constant file
from networksecurity.constant.training_pipeline import TARGET_COLUMN

#  i alos require my data transformation imputer params from constant file which is aplyed inside my knn imputer 
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS


# they stores input and output data 
from networksecurity.entity.artifact_entity import (
    # for the output variable of this class
    DataTransformationArtifact,
    
    # for the input variable of this class
    # beacuse this class required inside dataTranformation
    DataValidationArtifact
)

from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException 


from networksecurity.logging.logger import logging

#  importing the read yaml file from utils
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_object









# lets start the data transformation part

# these are the two details that i need to initailise before moving the ahead(to initialise the pipeline ) .data_validation_artifact from the previous components, data_transformation_config to basically initialise the data transformation class 
class DataTransformation:
    def __init__(self,data_validation_artifact:DataValidationArtifact,
                 data_transformation_config:DataTransformationConfig):
        try:
            # from  previous state 
            self.data_validation_artifact:DataValidationArtifact=data_validation_artifact
            # i 
            self.data_transformation_config:DataTransformationConfig=data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)


# just to read the csv files 
# we just dont need to to create object of this class 
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)




# this function will return the pipeline object the pipeline will have knn imputer object inside it  to work with missing values     
# 
    def get_data_transformer_object(cls)->Pipeline:
        """
        It initialises a KNNImputer object with the parameters specified in the training_pipeline.py file
        and returns a Pipeline object with the KNNImputer object as the first step.

        Args:
          cls: DataTransformation

        Returns:
          A Pipeline object
        """
        logging.info("Entered get_data_trnasformer_object method of Trnasformation class")
        # we are knn ipmuter to fill the missing values
        try:
        # we have alredy defined DATA_TRANSFORMATION_IMPUTER_PARAMS parameter so not need to define it again 
           imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
           logging.info(
                f"Initialise KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}"
            )
        #    we are creating the processor object which is of pipeline type
           processor:Pipeline=Pipeline([("imputer",imputer)])
           return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys)


# 1st
# lets initiate data transformation 
# whose return type is DataTransformationArtifact 
    def initiate_data_transformation(self)->DataTransformationArtifact:
        logging.info("Entered initiate_data_transformation method of DataTransformation class")
        try:
            # getting the train and test file path from data validation artifacts
            logging.info("Starting data transformation")
            train_df=DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)


            
            #### training dataframe
            # creating the depedant and indipandent feature 
            #  drop targer column from the data set
            # input_feature_train_df -> input feature training dataframe
            input_feature_train_df=train_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            # replace -1 with 0 in target column (this is for binary classification so we are replacing -1 with 0 to deal with 0 and 1 only )
            target_feature_train_df = target_feature_train_df.replace(-1, 0)


            
            #testing dataframe
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            # step 2  (**** this is way to call the function within the class  *****) 
            # data transformation object is initialised here to preprocessors pipeline object
            preprocessor=self.get_data_transformer_object()

            # fit the preprocessor object on the input feature training dataframe
            # and then transform the input feature training dataframe and testing dataframe
            preprocessor_object=preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature=preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature =preprocessor_object.transform(input_feature_test_df)
             
            # np.c_ is used to concatenate two numpy arrays (transformed_input_train_feature + target_feature_train_df )
            # transformed_input_test_feature + target_feature_test_df
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df) ]
            test_arr = np.c_[ transformed_input_test_feature, np.array(target_feature_test_df) ]


            # saving all the numpy array data and preprocessor object
            #save numpy array data
            save_numpy_array_data( self.data_transformation_config.transformed_train_file_path, array=train_arr, )
            save_numpy_array_data( self.data_transformation_config.transformed_test_file_path,array=test_arr,)
            save_object( self.data_transformation_config.transformed_object_file_path, preprocessor_object,)



# ==================================================================model pusher============================================================================================
            
            # saving the pickle file of preprocessor object
            save_object( "final_model/preprocessor.pkl", preprocessor_object,)
# ==================================================================model pusher============================================================================================
 

            #preparing artifacts
            # this is my output of this  data transform function 
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact



        except Exception as e:
            raise NetworkSecurityException(e,sys)
