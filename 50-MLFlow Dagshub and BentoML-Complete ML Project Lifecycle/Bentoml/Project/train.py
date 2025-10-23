import bentoml
# 




# using sklearn to train a simple model
from sklearn import svm
from sklearn import datasets
# Load training data set
iris = datasets.load_iris()
X, y = iris.data, iris.target

# Train the model
clf = svm.SVC(gamma='scale')
clf.fit(X, y)

# Save model to the BentoML local model store
# it wwill save some local cloud metadata as well
saved_model = bentoml.sklearn.save_model("iris_clf", clf)
print(f"Model saved: {saved_model}")



# this is format in which you can load the model back beacuase it will be get saved in local bentoml model store

## iris_clf:ilwg3wzz6sj4nthz6




