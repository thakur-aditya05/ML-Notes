

# importing necessary libraries 
import os
import sys


# importing exception and logging module
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging


# importing artifact and config entity
from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig


# importing util functions
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


# we are going to import save object and lode object 
from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
# to track the accuracy metrics 
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score




# importing ML algorithms to train the model 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

# importing mlflow for tracking the experiments 
import mlflow
from urllib.parse import urlparse

# to maintain the mlflow experiment tracking in dagshub
import dagshub
#dagshub.init(repo_owner='krishnaik06', repo_name='networksecurity', mlflow=True)



# these few code is added to set the environment variables for mlflow tracking in dagshub 
os.environ["MLFLOW_TRACKING_URI"]="https://dagshub.com/krishnaik06/networksecurity.mlflow"
os.environ["MLFLOW_TRACKING_USERNAME"]="krishnaik06"
os.environ["MLFLOW_TRACKING_PASSWORD"]="7104284f1bb44ece21e0e2adb4e36a250ae3251f"




# step A of model trainer 
class ModelTrainer:
    
    #   step 1A 
    # data_transformation_artifact from previous component 
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    
    
    
    
    
    
    # this is the function to track the mlflow experiments 
    # passing the best model and classification metric 
    def track_mlflow(self,best_model,classificationmetric):
        mlflow.set_registry_uri("https://dagshub.com/krishnaik06/networksecurity.mlflow")
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        # MLflow experiment tracking
        with mlflow.start_run():
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score
            # we are logging the metrics deatails
            # we all commute thses scores 1st 
            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision",precision_score)
            mlflow.log_metric("recall_score",recall_score)
            mlflow.sklearn.log_model(best_model,"model")
            
            # Model registry does not work with file store
            if tracking_url_type_store != "file":
                # Register the model
                # There are other ways to use the Model Registry, which depends on the use case,
                # please refer to the doc for more information:
                # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                mlflow.sklearn.log_model(best_model, "model", registered_model_name=best_model)
            else:
                mlflow.sklearn.log_model(best_model, "model")








    
    
    # step 2 
    # training the model with different algorithms and do the evaluation 
    # 
    def train_model(self,X_train,y_train,x_test,y_test):
        # initialize the models and their hyperparameters (verbose=1 for logging purpose of the model training)
        models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }
        
        # params for hyperparameter tuning 
        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32,128,256]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            }
            
        }
        # evalute the model 
        model_report:dict=evaluate_models(X_train=X_train, y_train=y_train,  X_test=x_test, y_test=y_test, models=models,param=params)
        
        
        
        
        
        ## To get best model score from dict
        best_model_score = max(sorted(model_report.values()))



        ## To get best model name from dict
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]
        
        # prediction using best model for train and test data
        y_train_pred=best_model.predict(X_train)

        # this  is to print the classification metrics for train data
        # this matrix will be used in the logging and tracking purpose in mlfow 
        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)
        
# ==================================================================mlflow============================================================================================
        ## Track the experiements with mlflow 
        self.track_mlflow(best_model,classification_train_metric)
# ==================================================================mlflow============================================================================================

        # prediction for test data
        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

# ==================================================================mlflow============================================================================================
        self.track_mlflow(best_model,classification_test_metric)
# ==================================================================mlflow============================================================================================

        # load the pkl file of preprocessor (loading the pickle file in this preprocessor variable)
        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        
        
        # importing the NetworkModel class to save the model and preprocessor together 9
        # saving the model pkl file and preprocessor pkl file together in a single pkl file
        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path,obj=NetworkModel)
        
          
# ==================================================================model pusher============================================================================================
        # model pusher
        # this is to save the model in the final model folder (best model file is getting save here)
        save_object("final_model/model.pkl",best_model)
# ==================================================================model pusher============================================================================================
        

        
        # 
        ## Model Trainer Artifact
        # all the parameter required in model trainer artifact 
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                            train_metric_artifact=classification_train_metric,
                            test_metric_artifact=classification_test_metric)
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        
        # 
        return model_trainer_artifact


        


       
    
    
    # step 2A of model trainer 
    # return type model trainer artifacts 
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        
        # we load the data from data transformation artifact 
        try:
            # loading transformed train and test file path 
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            # splitting the data into input and target feature
            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1], # x_train
                train_arr[:, -1], #  y_train
                test_arr[:, :-1],  # x_test
                test_arr[:, -1],  # y_test
            )
            
            # step 3A of model trainer 
            # we are training the model here 
            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            
            # returning the model trainer artifact 
            return model_trainer_artifact

            
        except Exception as e:
            raise NetworkSecurityException(e,sys)