#!/usr/bin/env python3

import os
import sys

class SimpointRes:
    nowline = 0
    oldline = 0
    weight  = 0
    def __init__(self, nowline, oldline, weight):
        self.nowline = nowline
        self.oldline = oldline
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
    res = {}
    for line in lines:
        v1 = line.split(" ")[0]
        v2 = int(line.split(" ")[1])
        res[v2] = v1
    return res

def read_select_file(filename):
    file1 = open(filename) 
    res = []
    while 1:
        line = file1.readline()
        if not line:
            break
        res.append(int(line))
    return res

def trans_simpoint_weight(simname, weightname, bbvselectname):
    sims = read_simres_files(simname) 
    weights = read_simres_files(weightname) 
    bbvsel = read_select_file(bbvselectname)
    
    if len(sims.keys()) != len(weights.keys()):
        print("simpoint file and weight file have different line number\n")
        exit()
    res = []
    for key in sims.keys():
        nowline = int(sims[key])    #simpoint从0开始
        oldline = bbvsel[nowline]
        weight = float(weights[key])
        res.append(SimpointRes(nowline, oldline, weight))
    return res

# -----------------------------------------------------------------
def save_newbbv(simres, filename):
    savename = filename+".simpoint"
    f1 = open(savename, 'w')
    idx = 0
    while idx < len(simres):
        line = str(simres[idx].oldline) + " " + str(idx) +"\n"
        f1.write(line)
        idx = idx + 1
    f1.close()

    savename = filename+".total"
    f1 = open(savename, 'w')
    idx = 0
    simres1 = sorted(simres, reverse=True)
    while idx < len(simres1):
        line = str(simres1[idx].oldline) + " " + str(simres1[idx].weight) +"\n"
        f1.write(line)
        idx = idx + 1
    f1.close()

    print("back labels simpoint file is saved in "+filename+".simpoint")
    print("back labels simpoint total file is saved in "+filename+".total")


#----------------------------------------------------------------------------------#

if len(sys.argv) < 4: 
    print("parameters are not enough.\n ./back_select_bbv.py simpointfile weightfile bbv.selected respath")
    exit()

if not os.path.exists(sys.argv[1]):
    print(sys.argv[1]+" is not exist.")
    exit()

if not os.path.exists(sys.argv[2]):
    print(sys.argv[2]+" is not exist.")
    exit()

if not os.path.exists(sys.argv[3]):
    print(sys.argv[3]+" is not exist.")
    exit()

simres = trans_simpoint_weight(sys.argv[1], sys.argv[2], sys.argv[3])

respath=""
(filepath, tempfilename) = os.path.split(sys.argv[2])
filepref = tempfilename.split(".weight")[0]

if len(sys.argv) == 4:
    respath = filepath
else:
    if not os.path.exists(sys.argv[4]):
        os.makedirs(sys.argv[4])
    respath = sys.argv[4]

filename = respath + "/" + filepref
save_newbbv(simres, filename)
