#!/usr/bin/env python3

import os
import sys

class SimpointRes:
    nowline = 0
    weight  = 0
    def __init__(self, nowline, weight):
        self.nowline = nowline
        self.weight = weight

    def __eq__(self, other):
        return self.weight == other.weight

    def __le__(self, other):
        return self.weight < other.weight

    def __gt__(self, other):
        return self.weight > other.weight

def read_simres_files(filename):
    file1 = open(filename) 
    lines = []
    while 1:
        line = file1.readline()
        if not line:
            break
        lines.append(line)
    res = []
    for line in lines:
        res.append("")
    
    for line in lines:
        v1 = line.split(" ")[0]
        v2 = int(line.split(" ")[1])
        res[v2] = v1
    return res


def trans_simpoint_weight(simname, weightname):
    sims = read_simres_files(simname) 
    weights = read_simres_files(weightname) 
    
    if len(sims) != len(weights):
        print("simpoint file and weight file have different line number\n")
        exit()

    idx = 0
    res = []
    while idx < len(sims):
        nowline = int(sims[idx])    #simpoint从0开始
        weight = float(weights[idx])
        res.append(SimpointRes(nowline, weight))
        idx = idx + 1

    return res

# -----------------------------------------------------------------
def save_newres(simres, simname):
    filename = os.path.splitext(simname)[0]
    savename = filename+".total"
    f1 = open(savename, 'w')
    idx = 0
    simres1 = sorted(simres, reverse=True)
    while idx < len(simres1):
        line = str(simres1[idx].nowline) + " " + str(simres1[idx].weight) +"\n"
        f1.write(line)
        # print(str(simres1[idx].nowline) + " " + str(simres1[idx].weight))
        idx = idx + 1
    f1.close()


#----------------------------------------------------------------------------------#

if len(sys.argv) < 3: 
    print("parameters are not enough.\n ./combine_simres.py simpointfile weightfile")
    exit()

if not os.path.exists(sys.argv[1]):
    print(sys.argv[1]+" is not exist.")
    exit()

if not os.path.exists(sys.argv[2]):
    print(sys.argv[2]+" is not exist.")
    exit()

simres = trans_simpoint_weight(sys.argv[1], sys.argv[2])
save_newres(simres, sys.argv[1])
