#!/usr/bin/python3

import numpy as np
import os
import sys
import math

class BBVData:
    labels = []
    values = []
    def __init__(self):
        self.values = []
        self.labels = []

    def addinfo(self, info):
        label = int(info.split(":")[1])
        value = float(info.split(":")[2])
        self.values.append(value)
        self.labels.append(label)


def read_bbv(filename):
    file1 = open(filename) 
    bbvs = []
    while 1:
        line = file1.readline()
        if not line:
            break

        if line[0] != 'T':
            print("there is a line without T as start!")
            print(line)
            exit()
        
        infos = line[1:].split(" ")
        bdata = BBVData()
        for info in infos:
            if ":" in info:
                bdata.addinfo(info)
        bbvs.append(bdata)
    file1.close()
    return bbvs


def cal_vec_dis(label1, vec1, label2, vec2):
    datas1 = {}
    datas2 = {}
    idx = 0
    while idx < len(label1):
        datas1[label1[idx]] = vec1[idx]
        idx = idx + 1

    idx = 0
    while idx < len(label2):
        datas2[label2[idx]] = vec2[idx]
        idx = idx + 1

    value = 0
    for l in label1:
        if l in datas2.keys():
            value = value + abs(datas1[l]-datas2[l])
        else:
            value = value + datas1[l]

    for l in label2:
        if l not in datas1.keys():
            value = value + datas2[l]

    return value
    
def normalized_matrix(mdatas):
    minv = min(mdatas[0])
    maxv = max(mdatas[0])
    for datas in mdatas:
        minv = min(minv, min(datas))
        maxv = max(maxv, max(datas))
    print(minv, maxv)

    idx = 0
    while idx < len(mdatas):
        idx1 = 0
        while idx1 < len(mdatas[idx]):
            mdatas[idx][idx1] = (mdatas[idx][idx1] - minv)/(maxv-minv)
            idx1 = idx1 + 1
        idx = idx + 1
    return mdatas


def cal_bbv_dis(bbvs):
    dis_matrix = []
    idx = 0
    while idx < len(bbvs):
        idx1 = 0
        rowdata = []
        while idx1 < len(bbvs): 
            rowdata.append(cal_vec_dis(bbvs[idx].labels, bbvs[idx].values, bbvs[idx1].labels, bbvs[idx1].values))
            idx1 = idx1 + 1
        idx = idx + 1
        dis_matrix.append(rowdata)
    return normalized_matrix(dis_matrix)

def save_dis_matrix(matrix, resname):
    f1 = open(resname, 'w')
    for row in matrix:
        str1 = ""
        for value in row:
            str1 = str1 + str(round(value, 4)) + ","
        f1.write(str1+"\n")
    f1.close()


if len(sys.argv) < 2: 
    print("parameters are not enough.\n ./cal_bbv_distance.py file.bbv")
    exit()

bbvfile = sys.argv[1]
if not os.path.exists(bbvfile):
    print(bbvfile+" is not exist.")
    exit()

bbvs = read_bbv(bbvfile)
dis_matrix = cal_bbv_dis(bbvs)

(filepath, tempfilename) = os.path.split(bbvfile)
(filepref, filesuff) = os.path.splitext(tempfilename)

resname = filepref+".bbv_dis"
save_dis_matrix(dis_matrix, resname)

