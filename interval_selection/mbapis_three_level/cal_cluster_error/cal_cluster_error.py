#!/usr/bin/env python3

import numpy as np
import csv
import os
import sys
import math

class LineData:
    values = []
    def __init__(self):
        self.values = []

    def addinfo(self, value):
        if isinstance(value, str):
            self.values.append(float(value))
        else:
            self.values.append(value)
    

class SimpointRes:
    place = 0
    weight = 0
    def __init__(self, place, weight):
        self.place = place
        self.weight = weight

class EventRes:
    name = 0
    meanv = 0
    def __init__(self, name, meanv):
        self.name = name
        self.meanv = meanv

datas = {}
def readdata(filename):
    f = open(filename, 'r')
    reader = csv.reader(f)
    for row in reader:
        temp = LineData()
        idx = 1
        while idx < len(row):
            if len(row[idx]) > 0:
                temp.addinfo(row[idx])
            idx = idx + 1
        if len(row[0]) == 0:
            row[0] = "stage"
        datas[row[0]] = temp
    f.close()

def readsimpoint(filename):
    simpointres = []
    file1 = open(filename) 
    while 1:
        line = file1.readline()
        if not line:
            break
        words = line.split(" ")
        place = words[0]
        weight = 0
        if len(words) > 1:
            weight = words[1]
        simpointres.append(SimpointRes(int(place), float(weight)))
    file1.close()
    return simpointres

def readeventlist(filename):
    eventlist = []
    file1 = open(filename) 
    while 1:
        line = file1.readline()
        if not line:
            break
        eventlist.append(line.split("\n")[0])
    file1.close()
    return eventlist

def getEventMeans(eventlist, simres):
    res = []
    for event in eventlist:
        if event not in datas.keys():
            continue
        val = 0
        for info in simres:
            if info.place >= len(datas[event].values):
                print("simpoint is too large")
                exit()
            val = val + info.weight * datas[event].values[info.place]
        res.append(EventRes(event, val))
    return res

def cmpEventMeans(simres, baseres):
    res = []
    idx = 0
    while idx < len(simres):
        val = 0
        if baseres[idx].meanv != 0:
            val = (simres[idx].meanv - baseres[idx].meanv) / baseres[idx].meanv
        res.append(val)
        idx = idx + 1
    return res


def saveCmpRes(filename, simres, baseres, cmpres):
    lines = []
    str1 = "eventname, baseres, simpointres, errorRate"
    lines.append(str1)

    idx = 0
    while idx < len(simres):
        str1 = simres[idx].name + "," + str(baseres[idx].meanv) + ","
        str1 = str1 + str(simres[idx].meanv) + "," + str(cmpres[idx])
        lines.append(str1)
        idx = idx + 1

    f1 = open(filename, 'w')
    for line in lines:
        f1.write(line+"\n")
        # print(line)
    f1.close()

#-------------------------------------------------------------------------
def addExtraEvent(meanres):
    mset = {}
    for res in meanres:
        mset[res.name] = res.meanv

    meanres.append(EventRes('user_ipc', mset['insts'] / mset['cycles']))
    meanres.append(EventRes('icache_to_l2_rate', mset['icache_to_L2'] / mset['icache_access']))
    meanres.append(EventRes('itlb_to_ptw_rate', mset['itlb_to_ptw'] / mset['itlb_access']))
    meanres.append(EventRes('dcache_to_l2_rate', mset['dcache_to_L2'] / mset['dcache_access']))
    meanres.append(EventRes('dtlb_to_ptw_rate', mset['dtlb_to_ptw'] / mset['dtlb_access']))

    temp = mset['npc_from_f1'] + mset['npc_from_f2'] + mset['npc_from_f3'] + mset['npc_from_core']
    meanres.append(EventRes('npc_from_f1_rate', mset['npc_from_f1'] / temp))
    meanres.append(EventRes('npc_from_f2_rate', mset['npc_from_f2'] / temp))
    meanres.append(EventRes('npc_from_f3_rate', mset['npc_from_f3'] / temp))

    #topdown
    #first level
    coreWidth = 2
    total_slots = (mset['cycles'] * coreWidth)
    issue_uops = mset['iss_int_uops'] + mset['iss_fp_uops']
    recovery_lost = mset['recovery_cycles'] * coreWidth

    frontend_bound = mset['dec_uops_not_delivered'] / total_slots
    bad_speculation = (issue_uops - mset['insts'] + recovery_lost) / total_slots
    retire = mset['insts'] / total_slots
    backend_bound = (frontend_bound + bad_speculation + retire) * -1.0 + 1.0

    total_spec_lost = (issue_uops - mset['insts'] + recovery_lost)
    bad_spec_wpath = (issue_uops - mset['insts']) / total_spec_lost
    bad_spec_recovery = recovery_lost / total_spec_lost

    meanres.append(EventRes('l1_frontend_bound', frontend_bound))
    meanres.append(EventRes('l1_bad_speculation', bad_speculation))
    meanres.append(EventRes('l1_retire', retire))
    meanres.append(EventRes('l1_backend_bound', backend_bound))
    meanres.append(EventRes('l1_bad_spec_wpath', bad_spec_wpath))
    meanres.append(EventRes('l1_bad_spec_recovery', bad_spec_recovery))

    #second level
    fetch_latency = mset['fetch_lat_cause_cycles'] / mset['cycles']
    fetch_bandwidth = frontend_bound - fetch_latency

    commit_misp = mset['com_misp_br'] + mset['com_misp_jalr'] 
    exceptions = mset['misalign_excpt'] + mset['lstd_pagefault'] + mset['fetch_pagefault'] + mset['mini_exception']
    branch_mispredicts = (commit_misp / (commit_misp + exceptions)) * bad_speculation
    machine_clears = bad_speculation - branch_mispredicts

    execution_stall = (mset['no_exe_cycles'] - mset['iq_empty_cycles'] + mset['one_exe_cycles']) / mset['cycles']
    memory_bound = (mset['memstall_anyload_cycles'] + mset['memstall_stores_cycles']) / mset['cycles']
    core_bound = execution_stall - memory_bound

    meanres.append(EventRes('l2_fetch_latency', fetch_latency))
    meanres.append(EventRes('l2_fetch_bandwidth', fetch_bandwidth))
    meanres.append(EventRes('l2_branch_mispredicts', branch_mispredicts))
    meanres.append(EventRes('l2_machine_clears', machine_clears))
    meanres.append(EventRes('l2_memory_bound', memory_bound))
    meanres.append(EventRes('l2_core_bound', core_bound))


#--------------------------------------------------------------------------
if len(sys.argv) < 4: 
    print("parameters are not enough.\n ./cal_cluster_error.py events.list sampling_result.csv cluster_result.total (baseline_intevals.label)")
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

if len(sys.argv) == 5 and not os.path.exists(sys.argv[4]):
    print(sys.argv[4]+" is not exist.")
    exit()


eventlist = readeventlist(sys.argv[1])
readdata(sys.argv[2])
simres = readsimpoint(sys.argv[3])
baseres = []
if len(sys.argv) == 5:
    baseres = readsimpoint(sys.argv[4])
else:
    idx = 0
    while idx < len(datas['cycles'].values):
        baseres.append(SimpointRes(idx, 0))
        idx = idx + 1
    
idx = 0
w = 1.0/len(baseres)
while idx < len(baseres):
    baseres[idx].weight = w
    idx = idx + 1

simres_mean = getEventMeans(eventlist, simres)
baseres_mean = getEventMeans(eventlist, baseres)

addExtraEvent(simres_mean)
addExtraEvent(baseres_mean)

cmpres = cmpEventMeans(simres_mean, baseres_mean)


(filepath, tempfilename) = os.path.split(sys.argv[3])
(filepref, filesuff) = os.path.splitext(tempfilename)
respath = filepath
resname = respath + "/" + filepref + "_errorRate.csv"
print("errorRate log is saved in " + resname)
saveCmpRes(resname, simres_mean, baseres_mean, cmpres)
