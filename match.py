__author__ = 'GongLi'

import sift
import numpy as np
import pca
import utility as util
from collections import Counter
import copy

# build the hash structure
def match(X, Y):
    column = X.shape[1]
    rowX = X.shape[0]
    rowY = Y.shape[0]

    # find matches between rowX and rowY points
    # construct a matrix of 8 * column
    hashStructure = []
    for i in range(8):
        hashStructure.append([])

        for j in range(column):
            hashStructure[i].append([])

    # Put X into this HashTable
    for i in range(rowX):
        # process feature rowX[i]
        for j in range(column):
            value = int(X[i][j] * 4) - 1
            hashStructure[value][j].append(i)

    # Hash ech point of Y
    result = []

    for i in range(rowY):

        allCounts = Counter()

        for j in range(column):
            hashValue = int(Y[i][j] * 4) - 1
            potential = copy.deepcopy(hashStructure[hashValue][j])

            if hashValue != 0:
                potential += copy.deepcopy(hashStructure[hashValue - 1][j])
            if hashValue != 7:
                potential += copy.deepcopy(hashStructure[hashValue + 1][j])

            counts = Counter(potential)
            allCounts += counts

            del potential

        # Find the respective point for point Y[i]
        # threshold M = 30
        mostCommon = allCounts.most_common(1)
        if mostCommon[0][1] >= 30:
            result.append(mostCommon[0][0])
        else:
            result.append(-1)

        print "Y["+str(i)  +  "] " + str(mostCommon[0][1])  + " is matched to X["+str(result[-1])+"]"
        del allCounts
        del counts

        allCounts = None
        counts = None


    print "Yes"



if __name__ == "__main__":

    img1 = "data/crans_1_small.jpg"
    img2 = "data/crans_2_small.jpg"

    locations1, features1 = sift.siftFeature(img1)
    locations2, features2 = sift.siftFeature(img2)

    # use PCA to reduce dimensions
    numberOfFeaturesOne = locations1.shape[0]
    numberOfFeaturesTwo = locations2.shape[0]

    features = np.vstack((features1, features2))
    V, S, mean = pca.pca(features)

    pcaFeatures1 = pca.project(features1, V, 36)
    pcaFeatures2 = pca.project(features2, V, 36)

    # normalize features
    util.normalize(pcaFeatures1)
    util.normalize(pcaFeatures2)

    match(pcaFeatures1, pcaFeatures2)







