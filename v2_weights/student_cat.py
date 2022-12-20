# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from seaborn import load_dataset
from sklearn.model_selection import train_test_split
import pickle


quiz_data = pd.read_csv("recommendations.csv")
# Store features matrix in X
# Store features matrix in X
X= quiz_data.iloc[:, 10:11].values
#Store target vector in 
y= quiz_data.iloc[:, 11].values

# Splitting data into training and testing data

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state = 100)

KNeighborsClassifier(
    n_neighbors=7,          # The number of neighbours to consider
    weights='uniform',      # How to weight distances
    algorithm='auto',       # Algorithm to compute the neighbours
    leaf_size=30,           # The leaf size to speed up searches
    p=2,                    # The power parameter for the Minkowski metric
    metric='minkowski',     # The type of distance to use
    metric_params=None,     # Keyword arguments for the metric function
    n_jobs=None             # How many parallel jobs to run
)

# Creating a classifier object in sklearn
clf = KNeighborsClassifier(p=1)

# Fitting our model
clf.fit(X_train, y_train)

# Making predictions
predictions = clf.predict(X_test)

# Making your own predictions
ith_prediction = clf.predict([[0.5]])
print(ith_prediction)

# Measuring the accuracy of our model
from sklearn.metrics import accuracy_score
print(accuracy_score(y_test, predictions))

pickle.dump(clf, open('student_cat.pkl', 'wb'))

