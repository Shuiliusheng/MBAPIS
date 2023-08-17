#!/usr/bin/env python3

import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import MultipleLocator
import matplotlib.ticker as ticker
from matplotlib.backends.backend_pdf import PdfPages

import csv
import os
import sys
import math

from pyparsing import alphanums

# mpl.rcParams['font.sans-serif'] = ['Times New Roman']
# mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['axes.unicode_minus'] = False  

class LineData:
    value = []
    def __init__(self):
        self.value = []

    def addinfo(self, value):
        if isinstance(value, str):
            self.value.append(float(value))
        else:
            self.value.append(value)

    def op(self, other, optype):
        temp = LineData()
        idx = 0
        if isinstance(other, float) or isinstance(other, int):
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

        if isinstance(other, LineData):
            if len(other.value) != len(self.value):
                return temp
            while idx < len(self.value):
                if optype == "-":
                    val = self.value[idx] - other.value[idx]
                elif optype == "*":
                    val = self.value[idx] * other.value[idx]
                elif optype == "/":
                    val = 1.0 * self.value[idx] / other.value[idx]
                else:
                    val = self.value[idx] + other.value[idx]
                temp.addinfo(val)
                idx = idx + 1
        return temp

    def __add__(self, other):
        return self.op(other, "+")

    def __sub__(self, other):
        return self.op(other, "-")

    def __mul__(self, other):
        return self.op(other, "*")

    def __truediv__(self, other):
        return self.op(other, "/")

class ClusterRes:
    place = 0
    weight = 0
    def __init__(self, place, weight):
        self.place = place
        self.weight = weight

def read_sample_data(filename):
    f = open(filename, 'r')
    datas = {}
    reader = csv.reader(f)
    for row in reader:
        temp = LineData()
        idx = 1
        while idx < len(row):
            if len(row[idx]) > 0:
                temp.addinfo(row[idx])
            idx = idx + 1
        # datas.append(temp)
        if len(row[0]) == 0:
            row[0] = "stage"
        datas[row[0]] = temp
    f.close()
    return datas

def read_cluster_result(filename):
    cluster_res = []
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
        cluster_res.append(ClusterRes(int(place), float(weight)))
    file1.close()
    return cluster_res

#---------------------------------------------------------------------------#
def draw_interval_line(cluster_res, ax, miny, maxy):
    def topercet(value):
        return '%0.0f%%' % (100. * value)

    textnum = 0
    step = (maxy-miny)*0.85*0.04
    for res in cluster_res:
        ax.axvline(x=res.place, ymin=0, ymax=0.85, c="black", linestyle ='--', linewidth=0.8, alpha = 0.6)
        if res.weight > 0.1:
            ax.text(res.place, miny+(maxy-miny)*0.85-textnum*step, topercet(res.weight), c="black", alpha = 0.6, fontsize=8)
            textnum = textnum + 1

def setMaxMin(minvalue, maxvalue, nstep):
    step = (maxvalue - minvalue)/nstep
    t = math.pow(10, -1*math.floor(math.log10(step)))
    minval = int(minvalue*t)/t
    maxval = math.ceil(maxvalue*t)/t
    step = (maxval - minval)/nstep
    t = math.pow(10, -1*math.floor(math.log10(step)))
    newstep = round(step*t)
    if(newstep<step*t):
        step = newstep+0.5
    else:
        step = newstep
    step = step / t
    maxval = minval + step * nstep
    return minval, maxval, step

def draw_pecetage(sampledatas, cluster_res, xvalue, lnames, rnames, xlabel, ylabel1, ylabel2):
    def make_label(value, pos):
        return '%0.0f%%' % (100. * value)

    print("draw percetage: " + ylabel1 + " & " + ylabel2)
    fig, ax = plt.subplots(figsize=(12, 4))
    ccolors = plt.get_cmap('RdYlBu')(np.linspace(0.85, 0.15, len(lnames)+len(rnames)))
    
    bottom_value = sampledatas[lnames[0]]*0.0
    idx = 0
    while idx < len(lnames):

        ax.bar(xvalue, sampledatas[lnames[idx]].value, width=1.0, label=lnames[idx], color=ccolors[idx], bottom=bottom_value.value)
        bottom_value = sampledatas[lnames[idx]] + bottom_value
        idx = idx + 1
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(make_label))
    ax.yaxis.set_major_locator(MaxNLocator(11))
    ax.xaxis.set_major_locator(MaxNLocator(20))
    ax.set_xlim([0, max(xvalue)+5])
    ax.set_ylim([0,1.1])
    ax.set_yticks(np.arange(0, 1.1, 0.1)[0:11])
    ax.set_xlabel(xlabel, fontsize = 12, labelpad = 1)
    ax.set_ylabel(ylabel1, fontdict={"size": 12}, labelpad = 0)  
    ax.tick_params(axis="x", which="major", length=4, labelrotation=45, pad = 0.2, labelsize = 10)
    ax.tick_params(axis="y", which="major", length=4, pad = 0.1, labelsize = 10)
    ax.grid(axis='y', linestyle ='--', alpha = 0.5)
    draw_interval_line(cluster_res, ax, 0, 1.1)

    if len(rnames) != 0:
        ax2 = ax.twinx() 
        maxvalue = 0.0
        minvalue = min(sampledatas[rnames[0]].value)
        cidx = len(lnames)
        for line in rnames:
            maxvalue = max(maxvalue, max(sampledatas[line].value))
            minvalue = min(minvalue, min(sampledatas[line].value))
            ax2.plot(xvalue, sampledatas[line].value, '-', label=line, color=ccolors[cidx], lw = 2)
            cidx = cidx + 1
        
        ax2.yaxis.set_major_locator(MaxNLocator(11))
        minvalue, maxvalue, step = setMaxMin(minvalue, maxvalue, 10)
        ax2.set_ylim([minvalue, maxvalue+step])
        ax2.set_yticks(np.arange(minvalue, maxvalue+step, step)[0:11])
        ax2.tick_params(axis="y", which="major", length=4, pad = 0.2, labelsize = 10)
        ax2.set_ylabel(ylabel2, fontdict={"size": 12})

    fig.legend(loc='upper right', bbox_to_anchor=(1, 1.02),frameon=False, bbox_transform=ax.transAxes, ncol=(len(lnames)+len(rnames)))
    plt.subplots_adjust(bottom =0.15, left=0.06, right = 0.95, top=0.91)  
    return fig
    

def draw_lines(sampledatas, cluster_res, xvalue, lnames, rnames, xlabel, ylabel1, ylabel2):    
    print("draw line: " + ylabel1 + " & " + ylabel2)
    fig, ax = plt.subplots(figsize=(12, 4))
    ccolors = plt.get_cmap('Paired')(np.linspace(0.80, 0.10, len(lnames)+len(rnames)))
    
    cidx = 0
    maxvalue = 0.0
    minvalue = min(sampledatas[lnames[0]].value)
    for line in lnames:
        maxvalue = max(maxvalue, max(sampledatas[line].value))
        minvalue = min(minvalue, min(sampledatas[line].value))
        ax.plot(xvalue, sampledatas[line].value, '-', label=line, color=ccolors[cidx], lw = 2)
        cidx = cidx + 1
    
    ax.xaxis.set_major_locator(MaxNLocator(20))
    ax.yaxis.set_major_locator(MaxNLocator(11))
    ax.tick_params(axis="x", which="major", length=4, labelrotation=45, pad = 0.2, labelsize = 10)
    ax.tick_params(axis="y", which="major", length=4, pad = 0.2, labelsize = 10)
    ax.set_xlabel(xlabel, fontsize = 12, labelpad = 1)
    ax.set_ylabel(ylabel1, fontdict={"size": 12})
    
    ax.set_xlim([0, max(xvalue)+5])
    minvalue, maxvalue, step = setMaxMin(minvalue, maxvalue, 10)
    ax.set_ylim([minvalue, maxvalue+step])
    ax.set_yticks(np.arange(minvalue, maxvalue+step, step)[0:11])
    ax.grid(axis='y', linestyle ='--', alpha = 0.5)
    
    draw_interval_line(cluster_res, ax, minvalue, maxvalue+step)

    if len(rnames) != 0:
        ax2 = ax.twinx() 
        maxvalue = max(sampledatas[rnames[0]].value)
        minvalue = min(sampledatas[rnames[0]].value)
        cidx = len(lnames)
        for line in rnames:
            maxvalue = max(maxvalue, max(sampledatas[line].value))
            minvalue = min(minvalue, min(sampledatas[line].value))
            ax2.plot(xvalue, sampledatas[line].value, '-', label=line, color=ccolors[cidx], lw = 2)
            cidx = cidx + 1
        ax2.tick_params(axis="y", which="major", length=4, pad = 0.2, labelsize = 10)
        ax2.set_ylabel(ylabel2, fontdict={"size": 12})
        ax2.yaxis.set_major_locator(MaxNLocator(11))
        minvalue, maxvalue, step = setMaxMin(minvalue, maxvalue, 10)
        ax2.set_ylim([minvalue, maxvalue+step])
        ax2.set_yticks(np.arange(minvalue, maxvalue+step, step)[0:11])

    fig.legend(loc='upper right', bbox_to_anchor=(1, 1.02),frameon=False, bbox_transform=ax.transAxes, ncol=(len(lnames)+len(rnames)))
    plt.subplots_adjust(bottom =0.15, left=0.06, right = 0.95, top=0.91)  
    return fig

#---------------------------------------------------------------------------#

def draw_samplefigs(sampledatas, cluster_res):
    figs = []
    temp = sampledatas['stage'] - 1
    xvalue = temp.value
    xlabel = "Instruction Interval (200M)"

    leftnames = ['l1_retire', 'l1_frontend_bound', 'l1_bad_speculation', 'l1_backend_bound']
    figs.append(draw_pecetage(sampledatas, cluster_res, xvalue, leftnames, ['user_ipc'], xlabel, "Topdown-First Level", "User IPC"))

    leftnames = ['l2_memory_bound', 'l2_core_bound']
    figs.append(draw_pecetage(sampledatas, cluster_res, xvalue, leftnames, ['user_ipc'], xlabel, "execution stall", "User IPC"))

    leftnames = ['l2_branch_mispredicts', 'l2_machine_clears']
    figs.append(draw_pecetage(sampledatas, cluster_res, xvalue, leftnames, ['user_ipc'], xlabel, "Bad Speculation", "User IPC"))

    leftnames = ['com_misp_MPKI']
    figs.append(draw_lines(sampledatas, cluster_res, xvalue, leftnames, ['user_ipc'], xlabel, "MPKI", "User IPC"))
    

    leftnames = ['dcache_to_L2']
    figs.append(draw_pecetage(sampledatas, cluster_res, xvalue, leftnames, ['user_ipc'], xlabel, "DCache miss num", "User IPC"))
    return figs


if __name__ == "__main__":
    if len(sys.argv) < 3: 
        print("parameters are not enough.\n ./draw_cluster_result.py sampling_result.csv cluster_res.total respath")
        exit()

    if not os.path.exists(sys.argv[1]):
        print(sys.argv[1]+" is not exist.")
        exit()

    if not os.path.exists(sys.argv[2]):
        print(sys.argv[2]+" is not exist.")
        exit()

    respath=""
    (filepath, tempfilename) = os.path.split(sys.argv[2])
    (filepref, filesuff) = os.path.splitext(tempfilename)
    if len(sys.argv) == 3:
        respath = filepath
    else:
        if not os.path.exists(sys.argv[3]):
            os.makedirs(sys.argv[3])
        respath = sys.argv[3]

    sampledatas = read_sample_data(sys.argv[1])
    cluster_res = read_cluster_result(sys.argv[2])
    
    figs = draw_samplefigs(sampledatas, cluster_res)

    resname = respath + "/" + filepref + ".pdf"
    print("result pdf name: " + resname)
    pp = PdfPages(resname)
    idx = 0
    for fig in figs:
        idx = idx + 1
        pp.savefig(fig, bbox_inches='tight', dpi=200)
    pp.close()
