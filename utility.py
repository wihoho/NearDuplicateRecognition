__author__ = 'GongLi'

import numpy as np
import pickle


def normalize(X):
    row = X.shape[0]
    column = X.shape[1]

    maxValues = np.amax(X, axis=1)
    minValues = np.amin(X, axis=1)

    for i in range(row):
        for j in range(column):
            X[i][j] = (X[i][j] - minValues[i]) * 2.0 / (maxValues[i] - minValues[i])

def storeObject(fileName, obj):
    file = open(fileName, "w")
    pickle.dump(obj, file)
    file.close()

def loadObject(fileName):
    file = open(fileName, "r")
    obj = pickle.load(file)
    return obj
