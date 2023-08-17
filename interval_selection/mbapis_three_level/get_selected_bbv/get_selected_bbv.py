#!/usr/bin/env python3

import os
import sys

def read_bbv_file(bbvname):
    file1 = open(bbvname) 
    lines = []
    while 1:
        line = file1.readline()
        if not line:
            break
        lines.append(line)
    file1.close()
    return lines

def save_newbbv(bbvec, savename):
    f1 = open(savename, 'w')
    for line in bbvec:
        f1.write(line)
    f1.close()

# -----------------------------------------------------------------
def select_bbvec(bbvec, sel_file_name):
    sel_num = []
    file1 = open(sel_file_name) 
    while 1:
        line = file1.readline()
        if not line:
            break
        sel_num.append(int(line))
    file1.close()

    sbbvec = []
    #select bbv (from 0)
    for val in sel_num:
        if val < len(bbvec) and val >= 0:
            sbbvec.append(bbvec[val])
    return sbbvec

#----------------------------------------------------------------------------------#

if len(sys.argv) < 3: 
    print("parameters are not enough.\n ./get_selected_bbv.py total_bbv.bb selected_interval respath")
    exit()

if not os.path.exists(sys.argv[1]):
    print(sys.argv[1]+" is not exist.")
    exit()

if not os.path.exists(sys.argv[2]):
    print(sys.argv[2]+" is not exist.")
    exit()

respath=""
(filepath, tempfilename) = os.path.split(sys.argv[2])
# (filepref, filesuff) = os.path.splitext(tempfilename)
filepref=tempfilename
if len(sys.argv) == 3:
    respath = filepath
else:
    if not os.path.exists(sys.argv[3]):
        os.makedirs(sys.argv[3])
    respath = sys.argv[3]


bbvec = read_bbv_file(sys.argv[1])
sbbvec = select_bbvec(bbvec, sys.argv[2])

#save new bbv
savename = respath + "/" + filepref.split(".si")[0] + "_selected"+".bb"
save_newbbv(sbbvec, savename)

print("selected bbv is saved in " + savename)
