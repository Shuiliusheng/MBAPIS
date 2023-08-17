#!/usr/bin/python3
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_pdf import PdfPages

import csv
import os
import sys
import math
import struct

# from pyparsing import alphanums
mpl.rcParams['axes.unicode_minus'] = False  


def read_bbv_dis_csv(filename):
    file1 = open(filename) 
    matrix = []
    while 1:
        line = file1.readline()
        if not line:
            break

        infos = line.replace("\n", "").split(",")
        values = []
        for info in infos:
            if len(info) != 0:
                values.append(float(info))
        matrix.append(values)
    file1.close()
    return matrix

def read_cluster_result(filename):
    file1 = open(filename) 
    places = []
    weights = []
    while 1:
        line = file1.readline()
        if not line:
            break
        words = line.split(" ")
        place = words[0]
        weight = 0
        if len(words) > 1:
            weight = words[1]
        places.append(int(place))
        weights.append(float(weight))
    file1.close()
    return places, weights
 

def draw_target_matrix(matrix_data, places):
    fig, ax = plt.subplots(figsize=(12, 12))

    norm = mpl.colors.Normalize(vmin=0,vmax=1)
    cax = ax.matshow(matrix_data, interpolation ='nearest', norm = norm) 
    cbar = fig.colorbar(cax) 

    ax.set_xlabel("interval", fontsize = 8, labelpad = 1)
    ax.set_ylabel("interval", fontsize = 8, labelpad = 1)

    ax.xaxis.set_ticks_position('bottom')
    ax.invert_yaxis()

    if len(places) < 10:
        xlabels = []
        for place in places:
            xlabels.append("interval_"+str(place))
        xticks = np.arange(0, 1 * len(xlabels), 1)
        ax.set_xticks(xticks+0.3)
        ax.tick_params(axis=u'both', which=u'both', length=0)
        ax.set_xticklabels(xlabels, rotation=45, ha='right', fontsize=8)
    return fig

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

def draw_target_bbvdis(bbv_matrix, target_places):
    nmatrix = []
    for place1 in target_places:
        row = []
        if place1 >= len(bbv_matrix):
            place1 = len(bbv_matrix) - 1
        for place2 in target_places:
            if place1 >= len(bbv_matrix) or place2 >= len(bbv_matrix):
                print(place1, place2, len(bbv_matrix))
            if place2 >= len(bbv_matrix):
                place2 = len(bbv_matrix) - 1
            row.append(bbv_matrix[place1][place2])
        nmatrix.append(row)

    fig1 = draw_target_matrix(nmatrix, target_places)
    return fig1

if __name__ == "__main__":
    if len(sys.argv) < 3: 
        print("parameters are not enough.\n ./draw_bbv_dis.py bbv_maxtrix.bbv_dis cluster_res.total respath")
        exit()

    matrixfile = sys.argv[1]
    if not os.path.exists(matrixfile):
        print(matrixfile + " is not exist.")
        exit()


    totalfile = sys.argv[2]
    if not os.path.exists(totalfile):
        print(totalfile + " is not exist.")
        exit()

    bbv_matrix = read_bbv_dis_csv(matrixfile)
    places, weights = read_cluster_result(totalfile)
    fig1 = draw_target_bbvdis(bbv_matrix, places)

    respath=""
    (filepath, tempfilename) = os.path.split(totalfile)
    if len(sys.argv) == 3:
        respath = filepath
    else:
        if not os.path.exists(sys.argv[3]):
            os.makedirs(sys.argv[3])
        respath = sys.argv[3]
    (filepref, filesuff) = os.path.splitext(tempfilename)
    resname = respath + "/" + filepref+"_bbvdis.pdf"
    
    pp = PdfPages(resname)
    pp.savefig(fig1, bbox_inches='tight', dpi=300)
    pp.close()
    print("result pdf is in: ", resname)

