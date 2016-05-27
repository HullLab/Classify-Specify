#!/usr/bin/python

import glob
import os
import shutil
import sqlite3
import csv

# CHANGE THIS FILE
specFile = '4sq_classification_specify.csv'

if not os.path.exists('parsing'):
    os.mkdir('parsing')

exts = ('*.tif','*.jpg')
images = []
for ext in exts:
    images.extend(glob.glob(ext))
    
csvFile = open(specFile,'rb')
csvRead = csv.reader(csvFile)

objDict = {}

for row in csvRead:
    if not row[0] == 'object':
        objDict[row[0]] = (row[3],row[4],row[5],row[6])
    
for obj in objDict.keys():
    folderName = '_'.join([objDict[obj][0],objDict[obj][1],objDict[obj][2]])
    if folderName[-1] == '_':
        folderName = folderName[:-1]
        
    currFolder = os.path.join('parsing',folderName)
    if not os.path.exists(currFolder):
        os.mkdir(currFolder)

    confidenceDirs = ['very','somewhat','not']
    for conf in confidenceDirs:
        currConfFolder = os.path.join(currFolder,conf)
        if not os.path.exists(currConfFolder):
            os.mkdir(currConfFolder)

    # Copy over current image file to appropriate folder
    try:
        currFile = glob.glob('*'+obj+'*')[0]
    except:
        currFile = None
    objConf = objDict[obj][-1]
    dst = os.path.join(currFolder,objConf)
    if currFile:
        shutil.copy(currFile,dst)
