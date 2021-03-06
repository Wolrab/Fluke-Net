"""
@authors: Adicus Finkbeiner  (Using Dylan's model as a starting point and with assistance from Connor Barlow)
A simple example of the kmeans baseline
#! /usr/bin/env python3
"""

import torch
import argparse
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from kmeansDataset import PrototypicalDataset, ImageLoader
from strconv2d import StrengthConv2d
from utils import parse_filter_specs, visualize_embeddings, PerformanceRecord, AggregatePerformanceRecord
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score

#as of right now this function isn't used (it was replaced with lines 31 and 32)
def dataLoaderToNumpy(data):
    for i in enumerate(data):
        #i = i.numpy()
        i = np.asarray(i)
        
    return np.asarray(data)

    #runs kmeans on our dataset, the number of clusters is equal to the number of classes
def kMeans(train_set, dev_set, train_out, dev_out, mb):
    #converts our training and dev sets to numpy arrays of len n_samples and n_features to pass into kmeans
    n_classes = len(np.unique(dev_out)) 
    train_set2 = next(iter(train_set))[0].numpy()
    train_set2 = train_set2.reshape(len(train_set2), -1)
    train_set2 = train_set2.transpose()
    dev_set2 = next(iter(dev_set))[0].numpy()
    dev_set2 = dev_set2.reshape(len(dev_set2), -1)
    #dev_set2 = dev_set2.transpose()
    
    kmeans = MiniBatchKMeans(n_clusters=n_classes, batch_size=mb)
    kmeans.fit(train_set2, train_out)
    kmeans.labels_
    #creates a dictionary of clusters for each label
    labelDict = retrieveInfo(kmeans.labels_, dev_set2)
    classLabels = np.random.rand(len(kmeans.labels_))
    #opens output file
    f = open('modelBaselineOutput.txt', 'w')
    for i in range(len(kmeans.labels_)):
        classLabels[i]=classLabels[kmeans.labels_[i]]

    for i in enumerate(dev_set2):
        #temp = np.asarray(i)
        #np.delete(temp, 0)
        #temp = temp.reshape(len(temp),-1)
        #temp = np.asarray(i)
        #print(np.shape(temp))
        #print(temp)
        #prediction = kmeans.predict(temp)
        #print(prediction,':',classLabels[[prediction]], file = f)

    f.close()
    #outputting results to file
    plt.scatter(dev_set2[:, 0], dev_set2[:, -1])
    plt.scatter(kmeans.cluster_centers_[:,0], kmeans.cluster_centers_[:,1], c='red', marker='x')
    plt.title('Kmeans cluster')
    #plt.show()
    plt.savefig('table.jpg')

    #creates dictionary of clusters for each label
def retrieveInfo(cluster_labels, dev_set):
    temp = dev_set[:1]
    temp = temp.transpose()
    temp = temp.flatten()
    temp = temp.astype(np.int)
    referenceLabels = {}
    for i in range(len(np.unique(cluster_labels))):
        index = np.where(cluster_labels == i,1,0)
        num = np.bincount(temp[index == 1]).argmax()
        referenceLabels[i] = num

    return referenceLabels
    
    #finds the optimal number of clusters for the best prediction for our dataset, may be unneccessary
    #because our optimal number of clusters should be our number of classes
def findK(x):
    #silhouette_score is between -1 and 1, higher value means better matched to its cluster
    clusterRange = list (range(2,10))

    for n in clusterRange:
        kmeans = KMeans(n_clusters=n)
        preds = kmeans.fit_predict(x)
        centers = kmeans.cluster_centers_

        score = silhouette_score(x, preds)
        print("For n_clusters = {}, silhouette score is {})".format(n, score))

def parse_all_args():
    'Parses commandline arguments'
    parser = argparse.ArgumentParser()
    # Default arguments. This is only ok because we're running everything with scripts anyways
    parser.add_argument("input_path",help="The path to the data (directory)")
    parser.add_argument("train_path",help="The training set input/target data (csv)")
    parser.add_argument("dev_path",help="The development set input/target data (csv)")
    #parser.add_argument("test_path",help="The test set input/target data (csv)")
    parser.add_argument("out_path",help="The path for all of our model evaluations (directory)")
    parser.add_argument("-mb",type=int,\
            help="The size of the train/dev/test episodes (int) [default: 5]",default=5)
    parser.add_argument("-print_reports",type=bool,\
            help="Prints report information as well as storing it (bool) [default: True]",default=True)
    return parser.parse_args()

def main(argv):
    # parse arguments
    args = parse_all_args()

    train_set = PrototypicalDataset(args.input_path, args.train_path)
    dev_set = PrototypicalDataset(args.input_path, args.dev_path, apply_enhancements=False)

    # Use the same minibatch size to make each dataset use the same episode size
    train_loader = torch.utils.data.DataLoader(train_set, shuffle=True,
            drop_last=False, batch_size=args.mb, num_workers=0, pin_memory=True
            )
    dev_loader = torch.utils.data.DataLoader(dev_set, shuffle=True,
            drop_last=False, batch_size=args.mb, num_workers=0, pin_memory=True)

    train_out = AggregatePerformanceRecord("train",args.out_path,dbg=args.print_reports)
    dev_out = AggregatePerformanceRecord("dev",args.out_path,dbg=args.print_reports)
    test_out = PerformanceRecord("test",args.out_path,dbg=args.print_reports)
    
    pred = kMeans(train_loader, dev_loader, train_out, dev_out, args.mb)
    
if __name__ == "__main__":
    main(sys.argv)
