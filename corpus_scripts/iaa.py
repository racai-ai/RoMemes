import pandas as pd
import nltk
import argparse
import os
import sys

import sklearn

import numpy as np
np.seterr(divide='ignore', invalid='ignore')

def loadFile(fmeta):
    meta={}

    first=True

    with open(fmeta,"r") as f:
        for line in f :
            if first:
                first=False
                continue
            data=line.strip().split("\t")
            if len(data)<3: continue
            meta[data[0]]=data[1:]

    return meta

annotators={}
for i in range(1,6):
    annotators[i]=loadFile("iaa/metadata_{}.tsv".format(i))

for k in range(0,len(annotators[1][list(annotators[1].keys())[0]])):
#for k in range(4,len(annotators[1][list(annotators[1].keys())[0]])):
    print("Feature {}:".format(k))
    for i in range(1,6):
        for j in range(i+1,6):


            y1=[]
            y2=[]

            for f in annotators[i]:
                if f in annotators[j]:
                    y1.append(annotators[i][f][k])
                    y2.append(annotators[j][f][k])

            #print(y1)
            #print(y2)

            if len(y1)>1:

                iaa=0
                #if len(y1)>0: 
                iaa=sklearn.metrics.cohen_kappa_score(y1,y2)
                acc=sklearn.metrics.accuracy_score(y1,y2)

                print("{}\t{}\t{}\t{}\t{:.2f}\t{:.2f}".format(i,j,len(y1),len(y2),iaa.astype(float),acc.astype(float)))

                #print(y1)
                #print(y2)

    print("")
