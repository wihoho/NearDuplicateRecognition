__author__ = 'GongLi'

import os
import numpy as np
import sift
from scipy.cluster.vq import *
import utility as util
from sklearn.cluster import KMeans
import pca
from random import randint

class Graph:

    def __init__(self, numOfNodes):

        bagOfadj = []
        for i in range(numOfNodes):
            bagOfadj.append([])

        self.bagOfAdj = bagOfadj
        self.numOfNodes = numOfNodes

    def connect(self, w, v):
        if w == v:
            return

        if v not in self.bagOfAdj[w]:
            self.bagOfAdj[w].append(v)

        if w not in self.bagOfAdj[v]:
            self.bagOfAdj[v].append(w)

    def getAdj(self, w):
        if w > self.numOfNodes - 1:
            return None

        return self.bagOfAdj[w]

    def getNumOfEdges(self, w):
        lst = self.getAdj(w)

        if not lst:
            return 0

        return len(lst)

    def connectedComponent(self):
        self.marked = [False] * self.numOfNodes

        connectedComponentList = []
        for i in range(self.numOfNodes):
            if not self.marked[i]:
                lst = []
                self.dfs(i, lst)
                connectedComponentList.append(lst)

        return connectedComponentList

    def dfs(self, w, lst):

        aja = self.bagOfAdj[w]
        self.marked[w] = True
        lst.append(w)

        for potential in aja:
            if not self.marked[potential]:
                self.dfs(potential, lst)

class Video:

    def __init__(self, videoPath):
        self.videoPath = videoPath

        SIFTfeatures = [] #
        imageNames = [] # name of each image

        # Read in video frames
        for item in os.listdir(videoPath):
            imagePath = videoPath +"/"+ item
            locations, features = sift.siftFeature(imagePath)

            SIFTfeatures.append(features)
            imageNames.append(item)

        # Histogramize each image
        imageHistograms = []
        vocabulary = util.loadObject("data/voc.pkl")
        vocSize = len(vocabulary)

        for imageFeature in SIFTfeatures:
            histogram = self.buildHistogram(imageFeature, vocabulary)
            imageHistograms.append(histogram)

        imageHistograms = np.array(imageHistograms)

        self.imageNames = imageNames
        self.imageHistograms = imageHistograms
        self.SIFTfeatures = SIFTfeatures

        # Cluster frames
        self.numOfFrames = len(imageNames)
        self.numOfCentriods = int(self.numOfFrames / 6)

        kmeans = KMeans(init="k-means++", n_clusters=self.numOfCentriods, n_init=10)
        kmeans.fit(self.imageHistograms)
        cluster_centroids = kmeans.cluster_centers_

        # Get components of each cluter
        codes, distance = vq(self.imageHistograms, cluster_centroids)

        dict = {}
        indice = 0
        for code in codes:
            keys = dict.keys()
            if str(code) in keys:
                dict[str(code)].append(indice)
            else:
                dict[str(code)] = []
                dict[str(code)].append(indice)

            indice += 1

        # stack all SIFT features to perform PCA
        stackOfSIFTfeatures = SIFTfeatures[0]
        for eachFeature in SIFTfeatures[1:]:
            stackOfSIFTfeatures = np.vstack((stackOfSIFTfeatures, eachFeature))

        V,S, mean = pca.pca(stackOfSIFTfeatures)
        self.V = V

        # Perform near duplicate within each cluster
        KEYFRAMES = []

        keys = dict.keys()
        for key in keys:
            cluster = dict[key]
            clusterFeatures = []
            for i in cluster:
                clusterFeatures.append(self.SIFTfeatures[i])

            potentialKeyFrames = self.identifyKeyFrame(clusterFeatures, cluster)
            KEYFRAMES += potentialKeyFrames
            print cluster +": "+ potentialKeyFrames


        self.keyFrames = KEYFRAMES

        compressedHistogram = self.imageHistograms[KEYFRAMES[0]]
        compressedImageName = [self.imageNames[KEYFRAMES[0]]]

        for keyframe in KEYFRAMES[1:]:
            compressedHistogram = np.vstack((compressedHistogram, self.imageHistograms[keyframe]))
            compressedImageName.append(self.imageNames[keyframe])

        self.compressedHistogram = compressedHistogram
        self.compressedImageName = compressedImageName


    def buildHistogram(self, imageFeature, vocabulary):
        vocSize = len(vocabulary)
        histogram = np.zeros(vocSize)

        codes, distance = vq(imageFeature, vocabulary)
        for code in codes:
            histogram[code] += 1

        return histogram

    # SIFTFeatures is a list of SIFT feature of each image
    def identifyKeyFrame(self, SIFTFeatures, indices, threshold = 0.15):
        if len(indices) in [1,2]:
            lst = []
            lst.append(indices[0])
            return lst

        # build up graph structure
        numberOfNodes = len(SIFTFeatures)
        graph = Graph(numberOfNodes)

        for i in range(numberOfNodes):
            for j in range(i+1, numberOfNodes, 1):

                one = SIFTFeatures[i]
                two = SIFTFeatures[j]

                # check whether one and two are near duplicate
                pcaFeatures1 = pca.project(one, self.V, 36)
                pcaFeatures2 = pca.project(two, self.V, 36)

                # normalize features
                util.normalize(pcaFeatures1)
                util.normalize(pcaFeatures2)

                np.savetxt("pcafeature1", pcaFeatures1, delimiter="\t")
                np.savetxt("pcafeature2", pcaFeatures2, delimiter="\t")

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

                matchSize = len(lines)
                oneSize = one.shape[0]
                twoSize = two.shape[0]

                ratio = matchSize / float(min(oneSize, twoSize))

                if ratio > threshold:
                    graph.connect(i,j)

        # Find nodes with largest edges in each connected component
        connectedComponents = graph.connectedComponent()

        tempkeyFrames = []
        for component in connectedComponents:
            edges = []

            for node in component:
                edges.append(graph.getNumOfEdges(node))

            maxIndice = 0
            maxValue = edges[0]
            for i in range(1, len(edges), 1):
                if maxValue < edges[i]:
                    maxValue = edges[i]
                    maxIndice = i

            # random choose one if there are many within one component
            maxEdges = []
            for i in range(len(edges)):
                if edges[i] == maxValue:
                    maxEdges.append(i)

            if len(maxEdges) == 1:
                tempkeyFrames.append(component[maxIndice])
            else:
                maxEdgeSize = len(maxEdges)
                randomNumber = randint(0, maxEdgeSize - 1)
                tempkeyFrames.append(component[randomNumber])

        keyFrames = []
        for indice in tempkeyFrames:
            keyFrames.append(indices[indice])

        return keyFrames


if __name__ == "__main__":
    v = Video("videos/google glass")








