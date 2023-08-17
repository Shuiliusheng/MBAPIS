import os
import json
import sys
import struct
import numpy as np


class EventInfo:
    value = []
    totalvalue = 0
    name = ""
    def __init__(self, name):
        self.name = name
        self.value = []
        self.totalvalue = 0

    def addinfo(self, value):
        self.value.append(value)
        self.totalvalue += value

    def isThis(self, name):
        return (name == self.name)

    def op(self, other, optype):
        temp = EventInfo("none")
        idx = 0
        if isinstance(other, float) or isinstance(other, int):
            temp.name = "(" + self.name + optype + str(other) + ")"
            while idx < len(self.value):
                if optype == "-":
                    val = self.value[idx] - other
                elif optype == "*":
                    val = self.value[idx] * other
                elif optype == "/":
                    val = 1.0 * self.value[idx] / other
                else:
                    val = self.value[idx] + other
                temp.addinfo(val)
                idx = idx + 1
            
            if optype == "-":
                temp.totalvalue = self.totalvalue - other
            elif optype == "*":
                temp.totalvalue = self.totalvalue * other
            elif optype == "/":
                temp.totalvalue = 1.0 * self.totalvalue / other
            else:
                temp.totalvalue = self.totalvalue + other

        if isinstance(other, EventInfo):
            temp.name = "(" + self.name + optype + other.name + ")"
            if len(other.value) != len(self.value):
                return temp
            while idx < len(self.value):
                if optype == "-":
                    val = self.value[idx] - other.value[idx]
                elif optype == "*":
                    val = self.value[idx] * other.value[idx]
                elif optype == "/":
                    if other.value[idx] == 0:
                        print(self.name, "/", other.name, "div zero", self.value[idx] , other.value[idx])
                        val = 0
                    else:
                        val = 1.0 * self.value[idx] / other.value[idx]
                else:
                    val = self.value[idx] + other.value[idx]
                temp.addinfo(val)
                idx = idx + 1

            if optype == "-":
                temp.totalvalue = self.totalvalue - other.totalvalue
            elif optype == "*":
                temp.totalvalue = self.totalvalue * other.totalvalue
            elif optype == "/":
                temp.totalvalue = 1.0 * self.totalvalue / other.totalvalue
            else:
                temp.totalvalue = self.totalvalue + other.totalvalue
        return temp

    # 重载加减乘除运算
    def __add__(self, other):
        return self.op(other, "+")

    def __sub__(self, other):
        return self.op(other, "-")

    def __mul__(self, other):
        return self.op(other, "*")

    def __truediv__(self, other):
        return self.op(other, "/")


# ----------------------------------------------------------------------------------

# read the name of each hardware event
def read_eventlist(eventlist):
    if not os.path.exists(eventlist) :
        print("the file events.list is not in this directory!")
        return 0

    file1 = open(eventlist) 
    eventdict = {}
    while 1:
        line = file1.readline()
        if not line:
            break
        words = line.replace(" ", "").replace("\n", "").split(',')
        eventdict[words[0]] = words[1]
    file1.close()
    return eventdict


def cal_percentage(einfos):
    totalinfo = einfos[0]
    idx = 1
    while idx < len(einfos):
        totalinfo = totalinfo + einfos[idx]
        idx = idx + 1

    res = []
    idx = 0
    while idx < len(einfos):
        info = einfos[idx] / totalinfo
        info.name = einfos[idx].name + "_perc"
        res.append(info)
        idx = idx + 1
    return res

def cal_fraction(numerator, denominator, name):
    temp = numerator / denominator
    if len(name) != 0:
        temp.name = name
    return temp


# -----------------------------------------------------------------
def saveEventInfo(eventinfos, savename):
    f1 = open(savename, 'w')

    data = []
    str1 = ","
    idx = 0
    while idx < len(eventinfos[0].value):
        str1 = str1 + str(idx+1) + ","
        idx = idx + 1
    data.append(str1)

    for info in eventinfos:
        str1 = info.name + ","
        idx = 0
        while idx < len(info.value):
            str1 = str1 + str(info.value[idx])
            str1 = str1 + ","
            idx = idx + 1  
        data.append(str1)
    
    for d in data:
        f1.write(d + "\n")
    f1.close()
    print("sampling log is saved in the csv file :" + savename)

# get the hardware event values of each sampling point from logfile
def readEventInfo(filename, eventdict):
    file1 = open(filename) 
    eventinfos = []
    numline = 0
    while 1:
        line = file1.readline()
        numline += 1
        if not line:
            break
        if line.find("{") == -1 and line.find("}") == -1:
            continue

        if line.find("{") == -1 or line.find("}") == -1:
            print(numline, line)
            continue

        line = "{" + line.split("{")[1].split("}")[0] + "}"

        info = json.loads(line)

        typeinfo = info['type']
        if typeinfo == "max_inst" : 
            continue
        idx = 0
        while idx < len(eventinfos):
            if eventinfos[idx].isThis(typeinfo):
                break
            idx = idx + 1
        if idx == len(eventinfos):
            einfo = EventInfo(typeinfo)
            einfo.addinfo(info['value'])
            eventinfos.append(einfo)
        else:
            einfo = eventinfos[idx]
            einfo.addinfo(info['value'])

    file1.close()

    eventsets = {}
    for info in eventinfos:
        name = info.name.replace(" ", "")
        if name in eventdict:
            info.name = eventdict[name]
            eventsets[eventdict[name]] = info
        else:
            info.name = "unused"
    return eventinfos, eventsets
