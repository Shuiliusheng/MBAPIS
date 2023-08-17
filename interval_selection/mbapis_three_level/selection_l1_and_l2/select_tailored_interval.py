#!/usr/bin/env python3
import numpy as np
import csv
import os
import sys
import math

class IntervalInfo:
    value = 0
    label = 0
    def __init__(self, value, label):
        self.value = value
        self.label = label

    def __eq__(self, other):
        return self.value == other.value

    def __le__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

class LineData:
    values = []
    def __init__(self):
        self.values = []

    def addinfo(self, value):
        label = len(self.values)
        self.values.append(IntervalInfo(float(value), label))

    def getTopPerc(self, percetage):
        resvec = []
        svalues = sorted(self.values, reverse=True)
        snum = min(len(self.values), int(len(self.values) * percetage))
        idx = 0
        while idx < snum:
            resvec.append(svalues[idx].label)
            idx = idx + 1
        return resvec

    def getValues(self, labels):
        res = []
        for label in labels:
            res.append(round(self.values[label].value, 3))
        return res
        
def read_sampledata(filename):
    f = open(filename, 'r')
    reader = csv.reader(f)
    datas = {}
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
    return datas


def save_select_dinfo(sdatas, intervals, events, places, filename):
    lines = []
    str1 = "select_label,"
    for event in events:
        str1 = str1 + event + ",priority,"
    lines.append(str1)

    idx = 0
    while idx < len(intervals):
        interval = intervals[idx]
        str1 = str(interval) + ","
        
        eidx = 0
        while eidx < len(events):
            evalue = round(sdatas[events[eidx]].values[interval].value, 3)
            str1 = str1 + str(evalue) + "," + str(places[idx][eidx]) + ","
            eidx = eidx + 1
        lines.append(str1)
        idx = idx + 1

    
    f1 = open(filename, 'w')
    for line in lines:
        f1.write(line+"\n")
    f1.close()


def save_select_intervals(intervals, filename):
    f1 = open(filename, 'w')
    for value in intervals:
        f1.write(str(value)+"\n")
    f1.close()
      

def select_intervals(sdatas, events, percs):
    top_datas = []
    idx = 0
    while idx < len(events):
        data = sdatas[events[idx]].getTopPerc(percs[idx])
        top_datas.append(data)
        idx = idx + 1

    sel_intervals = []
    sel_evt_places = []
    idx = 0
    while idx < len(top_datas[0]):
        interval = top_datas[0][idx]
        places = []
        places.append(idx)

        sidx = 1
        while sidx < len(top_datas):
            if interval not in top_datas[sidx]:
                break
            else:
                places.append(top_datas[sidx].index(interval))
            sidx = sidx + 1
        
        if sidx == len(top_datas):
            sel_intervals.append(interval)
            sel_evt_places.append(places)
        idx = idx + 1

    # print(sel_intervals)
    return sel_intervals, sel_evt_places


if len(sys.argv) < 4 or len(sys.argv)%2 != 0: 
    print("parameters are not enough.\n ./select_tailored_interval.py sampling_result.csv event1 ratio1 event2 ratio2 (eventn ratio_n)")
    exit()

samplecsv=sys.argv[1]
if not os.path.exists(samplecsv):
    print(samplecsv+" is not exist.")
    print("run script\n ./select_tailored_interval.py sampling_result.csv event1 ratio1 event2 ratio2 (eventn ratio_n)")
    exit()

eventnum = (len(sys.argv) - 2)/2
events = []
top_percs = []
res_suffix = ""

idx = 0
while idx < eventnum:
    name = sys.argv[idx*2 + 2]
    value = float(sys.argv[idx*2 + 3])
    events.append(name)
    top_percs.append(value)
    print("requirements: ", name, value)
    res_suffix = res_suffix + "_" + name + "_" + str(value)
    idx = idx + 1


sdatas = read_sampledata(samplecsv)
for event in events:
    if event not in sdatas.keys():
        print(event + "is not in the " +  samplecsv)
        exit()

#select interval
sel_intervals, sel_evt_places = select_intervals(sdatas, events, top_percs)
print("total selected intervals number: ", len(sel_intervals))

#save intervals and detail information
(filepath, tempfilename) = os.path.split(samplecsv)
(filepref, filesuff) = os.path.splitext(tempfilename)
filepref = filepref.split("_eventinfo")[0]

intervalsname = "./" + filepref + res_suffix + ".si"
detailname = "./dinfo_" + filepref + res_suffix + ".csv"


save_select_intervals(sel_intervals, intervalsname)
save_select_dinfo(sdatas, sel_intervals, events, sel_evt_places, detailname)

print("\nselected labels is save in: " + intervalsname)
print("detailed select labels information is save in: " + detailname)

