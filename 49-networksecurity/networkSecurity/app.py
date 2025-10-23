# we was triggering the training pipeline from here(as similar we triggered the individual components from main.py files)

# this app.py file is similar to main.py file but here we are using fastapi to trigger the training pipeline
# this is the frontend app to trigger the training pipeline and prediction
# lets create a apis 






import sys
import os

import certifi
ca = certifi.where()


from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
import pymongo



from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline



# importing fastapi library
from fastapi.middleware.cors import CORSMiddleware 
from fastapi import FastAPI, File, UploadFile,Request


# we use univorn to run the app
# also remember that app_run is comming from uvicorn library
from uvicorn import run as app_run



from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

# to load the pickle file 
from networksecurity.utils.main_utils.utils import load_object

# 
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


# where the data will be stored in the mongodb database
from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

# we are using jinja2 template to show the html table and pages 
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")













# to read the cient mongo 
client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]



# this is the way to create fastapi app 
app = FastAPI()
origins = ["*"]


# this is the basics setupt for the fastapi app to show that we are access it in the browsers 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# get request and tag will be authentication
# to create the home route

# /docs is the default route to see the fastapi app in the browser (swagger ui) 
@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


# we need to train the entire pipeline from here when get equest is sended to /train route
@app.get("/train")
async def train_route():
    try:
        # initialize and initiate  the training pipeline
        train_pipeline=TrainingPipeline()
        # 
        train_pipeline.run_pipeline()
        # training is successful
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)

# before this we have to create a html template to show the prediction output in table format
# C:\Users\thaku\OneDrive\Desktop\udemy\dataScience\MySelf\49-networksecurity\networkSecurity\templates\table.html
# 2
# we have text.csv file  where we need to predict the output
# we are going to create a post request to send the file to the api and get the


@app.post("/predict")
# test.csv is the file name
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        # reading this entire csv file
        df=pd.read_csv(file.file)
        #print(df)
        # loading the preprocessor and model object pkl file
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        # we are going to create a network model object which have predict method to predict the output passing the final model and preprocessor
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        print(df.iloc[0])
        # this is the custom predict method used to predict the output 
        y_pred = network_model.predict(df)
        print(y_pred)
        
        # adding a new column to the dataframe with the predicted output    beacuse this column was absent in the original csv file 
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        df.to_csv('prediction_output/output.csv') # converting the dataframe to csv file and saving it in prediction_output folder
        table_html = df.to_html(classes='table table-striped') # converting the dataframe to html table format
        #print(table_html)
        # return the html table to the browser
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)
# ------
# we are done in json and csv conversion both 
# ------



# this is run 1st and then everything else executed
# this is the entry point of the app 
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)
# to run the app use this command in the terminal
# uvicorn <file_name>:<app_name> --reload
# uvicorn app:app --reload


# /docs is the default route to see the fastapi app in the browser (swagger ui)
# 