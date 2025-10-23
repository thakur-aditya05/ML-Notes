import numpy as np
import bentoml

# this will be the wrapper arround the model
from bentoml.io import NumpyNdarray



# get the latest model from the local bentoml model store
iris_clf_runner = bentoml.sklearn.get("iris_clf:latest").to_runner()


# create a service with the runner under the the name of the iris classifier
# for mutli model you can pass multiple runners here as a list
svc = bentoml.Service("iris_classifier", runners=[iris_clf_runner])




# create an api endpoint for the service
# input and output will be numpy ndarray
@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
# then we will create a function which will take input and return the prediction
def classify(input_series: np.ndarray) -> np.ndarray:
    result = iris_clf_runner.predict.run(input_series)
    return result