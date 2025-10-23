









# it just adds acts like a decorator which probably creates a variable for an empty class 
# let iwe have a class we dont have any metjod and we needs to have some varibale defined 
from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    trained_file_path:str
    test_file_path:str
# just after train test split we have to get output of data ingestion 
# and output of data components will be train file path and test path 
# 
# yhis is usded in dataIngestion.py file
# -------------------------------------------------






# all these information should be return from data validation artifacts 
@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str

# our 2nd component output will be data validation artifact
# --------------------------------------------------





# step 2 of data transformation artifact
# these are my output of data transformation artifact 
# this is transformation artifact 
@dataclass
class DataTransformationArtifact:
    # pkl file path
    transformed_object_file_path: str
    # npy file path train 
    transformed_train_file_path: str
    # npy file path test
    transformed_test_file_path: str



# our 4th component output is 
# f1_score precision_score recall_score trained_model_file_path
# train_metric_artifact test_metric_artifact

# this is for calculating metrics 
@dataclass
class ClassificationMetricArtifact:
    f1_score: float
    precision_score: float
    recall_score: float



@dataclass
class ModelTrainerArtifact:
    # to store the trained model file path 
    trained_model_file_path: str
    # to store the metrics for train and test data 
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact
