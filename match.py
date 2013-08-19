__author__ = 'GongLi'

import sift
import numpy as np
import pca
import utility as util

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

# build the hash structure



