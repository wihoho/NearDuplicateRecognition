__author__ = 'GongLi'

import numpy as np

def normalize(X):
    row = X.shape[0]
    column = X.shape[1]

    maxValues = np.amax(X, axis=1)
    minValues = np.amin(X, axis=1)

    for i in range(row):
        for j in range(column):
            X[i][j] = (X[i][j] - minValues[i]) * 2.0 / (maxValues[i] - minValues[i])

