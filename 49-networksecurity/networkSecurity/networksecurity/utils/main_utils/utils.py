import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os,sys
import numpy as np
#import dill   # use for picklling of the file  
import pickle

from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV





# to read the yaml file 1st function use 
# give the yaml file path and return value of dict 
def read_yaml_file(file_path: str) -> dict:
    try:
        # we are openning in the read byte mode 
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e





def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)



# 4th compont data transformation
# to save test and train numpy array data
def save_numpy_array_data(file_path: str, array: np.array):
    """
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e




# to save any kind of object file like model file or preprocessor file
# knn impputer file is applied which will create pickle fiile 
# we are here creating the same directory if not present
def save_object(file_path: str, obj: object) -> None:
    try:
        logging.info("Entered the save_object method of MainUtils class")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            # dumping the pickle file
            pickle.dump(obj, file_obj)
        logging.info("Exited the save_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
# -----------------------------------------------------------------





# to load the object file like model pkl  file or preprocessor file 
# 1st time use in the model trainer component 
# to load the pkl file 
def load_object(file_path: str, ) -> object:
    try:
        if not os.path.exists(file_path):
            raise Exception(f"The file: {file_path} is not exists")
        with open(file_path, "rb") as file_obj:
            print(file_obj)
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


# this is also used in model trainer component 
# in data ingestion we are using load data numpy array data function  
def load_numpy_array_data(file_path: str) -> np.array:
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    







# this is the function used in model trainer component to evaluate the models
# this will give the report of the models

def evaluate_models(X_train, y_train,X_test,y_test,models,param):
    try:
        report = {}

        # go through the list of the all model 
        for i in range(len(list(models))):
            # take all the models values 
            model = list(models.values())[i]
            # take indiviadual params 
            para=param[list(models.keys())[i]]

            # apply the grid search cv 
            gs = GridSearchCV(model,para,cv=3)
            gs.fit(X_train,y_train)

            # set the best params 
            model.set_params(**gs.best_params_)
            # using that param train the model 
            model.fit(X_train,y_train)

            #model.fit(X_train, y_train)  # Train model

            # pridction for the train and test data 
            y_train_pred = model.predict(X_train)

            y_test_pred = model.predict(X_test)

            # get the r2 score for the train and test data
            train_model_score = r2_score(y_train, y_train_pred)
            # get the r2 score for test data 
            test_model_score = r2_score(y_test, y_test_pred)
            # add the model report 
            # we are using test model score to compare the models
            report[list(models.keys())[i]] = test_model_score
        # return the report
        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)