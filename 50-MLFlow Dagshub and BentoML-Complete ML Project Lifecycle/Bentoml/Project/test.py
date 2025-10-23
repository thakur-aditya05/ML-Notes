import bentoml



# i want to get latest model under iris_clf to run  this code 
# convert this into the runner object
iris_clf_runner = bentoml.sklearn.get("iris_clf:latest").to_runner()

# init the local model
iris_clf_runner.init_local()


# /we passsed input in the form of 2d array and it will do pridiction 
print(iris_clf_runner.predict.run([[5.9, 3., 5.1, 1.8]]))





























