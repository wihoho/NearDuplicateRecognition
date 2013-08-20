__author__ = 'GongLi'

import sift
import numpy as np
import pca
import utility as util
from collections import Counter
import copy
import os
from pylab import *
from PIL import Image

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
            value = int(X[i][j] * 4)

            if value == 8:
                value = 7

            hashStructure[value][j].append(i)

    # Hash ech point of Y
    result = []

    for i in range(rowY):

        allCounts = Counter()

        for j in range(column):
            hashValue = int(Y[i][j] * 4);
            if hashValue == 8:
                hashValue = 7

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

    return result

def appendimages(im1,im2):
    """ Return a new image that appends the two images side-by-side. """

    # select the image with the fewest rows and fill in enough empty rows
    rows1 = im1.shape[0]
    rows2 = im2.shape[0]

    if rows1 < rows2:
        im1 = concatenate((im1,zeros((rows2-rows1,im1.shape[1]))),axis=0)
    elif rows1 > rows2:
        im2 = concatenate((im2,zeros((rows1-rows2,im2.shape[1]))),axis=0)
    # if none of these cases they are equal, no filling needed.

    return concatenate((im1,im2), axis=1)

def plotMatch(im1, im2, locations1, locations2, match):

    figure()
    gray()

    im3 = appendimages(im1, im2)
    im3 = np.vstack((im3, im3))

    imshow(im3)


    width = im1.shape[1]
    for m in match:
        i = m[0]
        j = m[1]

        loc1 = locations1[i]
        loc2 = locations2[j]

        plot([loc1[0], loc2[0] + width],[loc1[1], loc2[1]],'c')

    plot([0,200], [0,100], 'r--')

    axis('off')
    show()


# Remember to write a Java version to test

if __name__ == "__main__":

    img1 = "data/crans_1_small.jpg"
    img2 = "data/crans_2_small.jpg"

    image1 = np.array(Image.open(img1).convert("L"))
    image2 = np.array(Image.open(img2).convert("L"))

    locations1, features1 = sift.siftFeature(img1)
    locations2, features2 = sift.siftFeature(img2)

    # use PCAac to reduce dimensions
    numberOfFeaturesOne = locations1.shape[0]
    numberOfFeaturesTwo = locations2.shape[0]

    features = np.vstack((features1, features2))
    V, S, mean = pca.pca(features)

    pcaFeatures1 = pca.project(features1, V, 36)
    pcaFeatures2 = pca.project(features2, V, 36)

    # normalize features
    util.normalize(pcaFeatures1)
    util.normalize(pcaFeatures2)

    np.savetxt("data/pcafeature1", pcaFeatures1, delimiter="\t")
    np.savetxt("data/pcafeature2", pcaFeatures2, delimiter="\t")

    # interface with Java program to do matching
    rowX = pcaFeatures1.shape[0]
    rowY = pcaFeatures2.shape[0]
    column = pcaFeatures1.shape[1]

    matchCommand = "java match " +str(rowX)+ " " +str(rowY)+ " " +str(column)
    print matchCommand
    os.system(matchCommand)

    # plot according to match stored in "data" folder
    matchFile = open("data/match", 'r')
    lines = matchFile.readlines()

    matches = []
    for line in lines:
        temp = line.split(" ")
        tempTuple = (int(temp[0]), int(temp[1]))
        matches.append(tempTuple)

    plotMatch(image1, image2, locations1, locations2, matches)









