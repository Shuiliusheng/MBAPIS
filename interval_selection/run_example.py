#!/usr/bin/env python3
import os
import sys


def detect_file(filename):
    if not os.path.exists(filename):
        print(filename + " is not exist.")
        exit()

def create_dir(dirname):
    if not os.path.exists(dirname):
        os.system("mkdir -p "+dirname)

def mv_file(dstdir, filename):
    dstname = dstdir + "/" + filename
    os.system("mv " + filename + " " + dstname)
    return dstname


##### read the sampling log, transform to the csv file
logfile="./logfile/sampling_logs/gcc.log"
resultdir="./result/sampling_result"
detect_file(logfile)
create_dir(resultdir)

os.system("python3 ./read_sampling_log/read_sampling_log.py ./read_sampling_log/events.list "+logfile+" "+resultdir)

(filepath, temp) = os.path.split(logfile)
(benchname, filesuff) = os.path.splitext(temp)
sampling_csv = resultdir + "/" + benchname + "_eventinfo.csv"
detect_file(sampling_csv)


##### use MBAPIS to select representative and tailored intervals
select_l1_l2_py="./mbapis_three_level/selection_l1_and_l2/select_tailored_interval.py"
get_bbv_py="./mbapis_three_level/get_selected_bbv/get_selected_bbv.py"
back_interval_py="./mbapis_three_level/get_selected_bbv/back_interval_index.py"
simpoint_path="./mbapis_three_level/clustering_l3/Simpoint3.2/bin/simpoint"

resultdir="./result/mbapis_selected"

## select tailored intervals
event1="com_misp_MPKI"          #hardware event
ratio1="0.5"
event2="l2_branch_mispredicts"  #topdown
ratio2="0.5"
os.system(select_l1_l2_py + " " + sampling_csv + " " + event1 + " " + ratio1 + " " + event2 + " " + ratio2)
res_name = benchname + "_" + "com_misp_MPKI_0.5_l2_branch_mispredicts_0.5"
tailored_intervals = res_name + ".si"
tailored_intervals_dinfo = "dinfo_" + res_name + ".csv"

tailored_intervals = mv_file(resultdir, tailored_intervals)
tailored_intervals_dinfo = mv_file(resultdir, tailored_intervals_dinfo)


## get the new bbv file of tailored intervals
gcc_bbv_file = "./logfile/bbvfile/gcc_400B_200M.bb"  #400B_200M just is a suffix
new_bbv_file = resultdir + "/" + res_name + "_selected.bb"

os.system(get_bbv_py + " " + gcc_bbv_file + " " + tailored_intervals + " " + resultdir)
detect_file(new_bbv_file)

## clustering analysis, get representative tailored intervals
simpointname = res_name + ".simpoint"
weightname = res_name + ".weight"
os.system(simpoint_path + " -maxK 20 -loadFVFile " + new_bbv_file + " -saveSimpoints " + simpointname + " -saveSimpointWeights " + weightname + ">temp.log")
os.system("rm temp.log")
detect_file(simpointname)


## transform the positions of intervals selected by clustering analysis 
os.system(back_interval_py + " " + simpointname + " " + weightname + " " + tailored_intervals + " .")

mbapis_sintervals = res_name + ".total"
os.system("rm " + simpointname)
os.system("rm " + weightname)
detect_file(mbapis_sintervals)
mbapis_sintervals = mv_file(resultdir, mbapis_sintervals)


#### calculate mbapis estimated error
eventlist = "./mbapis_three_level/cal_cluster_error/events.list"
cal_err_py = "./mbapis_three_level/cal_cluster_error/cal_cluster_error.py"

os.system(cal_err_py + " " + eventlist + " " + sampling_csv + " " + mbapis_sintervals + " " + tailored_intervals)
mbapis_error_csv = resultdir + "/" + res_name + "_errorRate.csv"
detect_file(mbapis_error_csv)


#### draw plot
draw_events = "./drawplot/draw_cluster_result.py"
draw_bbvdis = "./drawplot/draw_bbv_dis.py"

os.system(draw_events + " " + sampling_csv + " " + mbapis_sintervals + " " + resultdir)
mbapis_fig_pdf1 = resultdir + "/" + res_name + ".pdf"

# calculated by the script in the cal_bbv_distance directory
gcc_bbvdis = "./logfile/bbvdis/gcc_400B_200M.bbv_dis"
os.system(draw_bbvdis + " " + gcc_bbvdis + " " + mbapis_sintervals + " " + resultdir)
mbapis_fig_pdf2 = resultdir + "/" + res_name + "_bbvdis.pdf"



###---------------------------------------------------------
##### simpoint results
simpoint_path = "./mbapis_three_level/clustering_l3/Simpoint3.2/bin/simpoint"
combine_res_py = "./mbapis_three_level/get_selected_bbv/combine_cluster_res.py"
gcc_bbv_file = "./logfile/bbvfile/gcc_400B_200M.bb"
resultdir = "./result/Simpoint_result"

resname = "gcc_simpoint"
simpointname = resname + ".simpoint"
weightname = resname + ".weight"
os.system(simpoint_path + " -maxK 20 -loadFVFile " + gcc_bbv_file + " -saveSimpoints " + simpointname + " -saveSimpointWeights " + weightname + ">temp.log")
os.system("rm temp.log")
detect_file(simpointname)

## combine simpoint and weight to a file
totalfile = resname + ".total"
os.system(combine_res_py + " " + simpointname + " " + weightname)
detect_file(totalfile)
simpoint_intervals = mv_file(resultdir, totalfile)
os.system("rm " + simpointname)
os.system("rm " + weightname)

## calculate mbapis estimated error
eventlist = "./mbapis_three_level/cal_cluster_error/events.list"
cal_err_py = "./mbapis_three_level/cal_cluster_error/cal_cluster_error.py"

os.system(cal_err_py + " " + eventlist + " " + sampling_csv + " " + simpoint_intervals + " ")
simpoint_error_csv = resultdir + "/" + resname + "_errorRate.csv"
detect_file(simpoint_error_csv)

## draw plot
draw_events = "./drawplot/draw_cluster_result.py"
draw_bbvdis = "./drawplot/draw_bbv_dis.py"

os.system(draw_events + " " + sampling_csv + " " + simpoint_intervals + " " + resultdir)
simpoint_fig_pdf1 = resultdir + "/" + resname + ".pdf"

gcc_bbvdis = "./logfile/bbvdis/gcc_400B_200M.bbv_dis"
os.system(draw_bbvdis + " " + gcc_bbvdis + " " + simpoint_intervals + " " + resultdir)
simpoint_fig_pdf2 = resultdir + "/" + resname + "_bbvdis.pdf"


#### show result files
print("\n\n\n---------------------------------------------------------")
print("Result file name: ")
print("sampling result: " + sampling_csv)
print("MBAPIS -- selected tailored intervals (level1 & level2): " + tailored_intervals)
print("MBAPIS -- bbv of tailored intervals: " + new_bbv_file)
print("MBAPIS -- representative tailored intervals (level3): " + mbapis_sintervals)
print("MBAPIS -- mbapis estimated error for tailored intervals: " + mbapis_error_csv)
print("MBAPIS -- hardware event figures: " + mbapis_fig_pdf1)
print("MBAPIS -- bbv distance figure: " + mbapis_fig_pdf2 + "\n")


print("\n---------------------------------------------------------")
print("Simpoint -- selected intervals: " + simpoint_intervals)
print("Simpoint -- estimated error: " + simpoint_error_csv)
print("Simpoint -- hardware event figures: " + simpoint_fig_pdf1)
print("Simpoint -- bbv distance figure: " + simpoint_fig_pdf2 + "\n")