
# this is the file created to combine both the preprocessor and the model file used in model_training file 



# beacuse the reaons of the creating this specific file
# over here is basically to create this network 
# will give the deatils with respect to all the informaion that is there with respect to the model 



# this estimator.py file will give you deatils with respect to all the information that is there wrt the model  

# the processed pickle file and model pkl file both will be saved in the same file 
# the processed pickle file coming from the data transformation component 



# 


from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR,MODEL_FILE_NAME

import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkModel:
    def __init__(self,preprocessor,model):
        try:
            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        

# then we have to create the predict method  

# for every new data firstly we need to transform then predict 
    def predict(self,x):
        try:
            # for any new data point we have to first transform it 
            # this is way to create pre_processor pkl file 
            x_transform = self.preprocessor.transform(x)
            # then we have to predict it  
            y_hat = self.model.predict(x_transform)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e,sys)