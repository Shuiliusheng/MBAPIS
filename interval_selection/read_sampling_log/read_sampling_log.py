#!/usr/bin/env python3


import os
import json
import sys
import struct
import numpy as np

from event import *

#-------------------------------------------------------------------------------------
def process_infos(eventinfos, eventsets):

    # cal some hardware event values based on basic event values
    eventinfos.append(cal_fraction(eventsets['insts'], eventsets['cycles'], "user_ipc"))
    eventinfos.append(cal_fraction(eventsets['icache_access'] - eventsets['icache_hit'], eventsets['icache_access'], "icache_miss_rate"))
    eventinfos.append(cal_fraction(eventsets['icache_to_L2'], eventsets['icache_access'], "icache_to_l2_rate"))
    eventinfos.append(cal_fraction(eventsets['itlb_access'] - eventsets['itlb_hit'], eventsets['itlb_access'], "itlb_miss_rate"))
    eventinfos.append(cal_fraction(eventsets['itlb_to_ptw'], eventsets['itlb_access'], "itlb_to_ptw_rate"))

    eventinfos.append(cal_fraction(eventsets['dcache_nack_num'], eventsets['dcache_access'], "dcache_nack_rate"))
    eventinfos.append(cal_fraction(eventsets['dcache_to_L2'], eventsets['dcache_access'], "dcache_to_l2_rate"))
    eventinfos.append(cal_fraction(eventsets['dtlb_miss_num'], eventsets['dtlb_access'], "dtlb_miss_rate"))
    eventinfos.append(cal_fraction(eventsets['dtlb_to_ptw'], eventsets['dtlb_access'], "dtlb_to_ptw_rate"))

    eventinfos.append(cal_fraction(eventsets['brmask_stall'], eventsets['cycles'], "brmask_stall_cycle_rate"))
    eventinfos.append(cal_fraction(eventsets['dis_rob_stall'], eventsets['cycles'], "dis_rob_stall_cycle_rate"))
    eventinfos.append(cal_fraction(eventsets['spec_miss_issuop'], eventsets['iss_uop_num'], "misspec_issuop_rate"))
    eventinfos.append(cal_fraction(eventsets['rollback_cycles'], eventsets['cycles'], "rollback_cycles_rate"))

    eventinfos.append(cal_fraction(eventinfos[58] + eventinfos[59] + eventinfos[60] + eventinfos[61], eventinfos[1], "com_excpt_rate"))
    eventinfos.extend(cal_percentage(eventinfos[58:62]))  # exception rate

    eventinfos.append(cal_fraction((eventinfos[43] + eventinfos[44]) * 1000, eventinfos[1], "exe_misp_MPKI"))
    tinfos = []
    tinfos.append(eventsets['exe_misp_br'])   # exe mis br
    tinfos.append(eventsets['exe_misp_ret'])   # exe mis ret
    tinfos.append(eventsets['exe_misp_jalrcall'])   # exe mis jalrcall
    temp = eventsets['exe_misp_jalr'] - eventsets['exe_misp_ret'] - eventsets['exe_misp_jalrcall']
    temp.name = "exe_misp_jalr_else"
    tinfos.append(temp)   # exe mis else jalr
    eventinfos.extend(cal_percentage(tinfos[0:4]))  # exe misp rate

    eventinfos.append(cal_fraction((eventinfos[53] + eventinfos[54]) * 1000, eventinfos[1], "com_misp_MPKI"))
    tinfos1 = []
    tinfos1.append(eventinfos[53])   # com mis br
    tinfos1.append(eventinfos[55])   # com mis ret
    tinfos1.append(eventinfos[56])   # com mis jalrcall
    temp = eventinfos[54] - eventinfos[55] - eventinfos[56]
    temp.name = "com_misp_jalr_else"
    tinfos1.append(temp)   # exe mis else jalr
    eventinfos.extend(cal_percentage(tinfos1[0:4])) # com misp rate

    eventinfos.extend(cal_percentage(eventinfos[8:12]))   # npc source percentage
    eventinfos.extend(cal_percentage(eventinfos[12:15]))  # fb out percentage
    eventinfos.extend(cal_percentage(eventinfos[15:18]))  # dec out percentage
    eventinfos.extend(cal_percentage(eventinfos[20:23]))  # dis out percentage
    eventinfos.extend(cal_percentage(eventinfos[27:30]))  # iss out percentage
    eventinfos.extend(cal_percentage(eventinfos[31:33]))  # exe load store percentage
    eventinfos.extend(cal_percentage(eventinfos[47:49]))  # com load store percentage

    eventinfos.append(cal_fraction(eventsets['com_misp_br'] + eventsets['com_misp_jalr'], eventsets['com_is_br'] + eventsets['com_is_jalr'], "com_mispred_rate"))

    eventinfos.append(cal_fraction((eventsets['mini_exception']) * 1000, eventinfos[1], "mini_excpt_PKI"))
    eventinfos.append(cal_fraction((eventsets['misalign_excpt']) * 1000, eventinfos[1], "misalign_PKI"))
    eventinfos.append(cal_fraction((eventsets['lstd_pagefault']) * 1000, eventinfos[1], "lstd_pf_PKI"))
    eventinfos.append(cal_fraction((eventsets['fetch_pagefault']) * 1000, eventinfos[1], "fetch_pf_PKI"))

    #topdown calculation
    coreWidth = 2
    #first level
    total_slots = (eventsets['cycles'] * coreWidth)
    # issue_uops = eventsets['iss_int_uops'] + eventsets['iss_fp_uops']
    issue_uops = eventsets['dis_out_full'] * coreWidth + eventsets['dis_out_notFull']
    recovery_lost = eventsets['recovery_cycles'] * coreWidth

    frontend_bound = eventsets['dec_uops_not_delivered'] / total_slots
    bad_speculation = (issue_uops - eventsets['insts'] + recovery_lost) / total_slots
    retire = eventsets['insts'] / total_slots
    backend_bound = (frontend_bound + bad_speculation + retire) * -1.0 + 1.0

    frontend_bound.name = "l1_frontend_bound"
    bad_speculation.name = "l1_bad_speculation"
    retire.name = "l1_retire"
    backend_bound.name = "l1_backend_bound"
    eventinfos.extend([frontend_bound, bad_speculation, retire, backend_bound])

    total_spec_lost = (issue_uops - eventsets['insts'] + recovery_lost)
    bad_spec_wpath = (issue_uops - eventsets['insts']) / total_spec_lost
    bad_spec_recovery = recovery_lost / total_spec_lost
    bad_spec_wpath.name = "l1_bad_spec_wpath"
    bad_spec_recovery.name = "l1_bad_spec_recovery"
    eventinfos.extend([bad_spec_wpath, bad_spec_recovery])

    #second level
    fetch_latency = eventsets['fetch_lat_cause_cycles'] / eventsets['cycles']
    fetch_bandwidth = frontend_bound - fetch_latency
    fetch_latency.name = "l2_fetch_latency"
    fetch_bandwidth.name = "l2_fetch_bandwidth"
    
    commit_misp = eventsets['com_misp_br'] + eventsets['com_misp_jalr'] 
    exceptions = eventsets['misalign_excpt'] + eventsets['lstd_pagefault'] + eventsets['fetch_pagefault'] + eventsets['mini_exception']
    branch_mispredicts = (commit_misp / (commit_misp + exceptions)) * bad_speculation
    machine_clears = bad_speculation - branch_mispredicts
    branch_mispredicts.name = "l2_branch_mispredicts"
    machine_clears.name = "l2_machine_clears"

    mini_excpt_rate = (eventsets['mini_exception'] / exceptions) * machine_clears
    normal_excpt_rate = machine_clears - mini_excpt_rate
    mini_excpt_rate.name = "l2_ldstspec_excpt"
    normal_excpt_rate.name = "l2_normal_excpt"
    eventinfos.extend([mini_excpt_rate, normal_excpt_rate])

    execution_stall = (eventsets['no_exe_cycles'] - eventsets['iq_empty_cycles'] + eventsets['one_exe_cycles']) / eventsets['cycles']
    memory_bound = (eventsets['memstall_anyload_cycles'] + eventsets['memstall_stores_cycles']) / eventsets['cycles']
    core_bound = execution_stall - memory_bound
    memory_bound.name = "l2_memory_bound"
    core_bound.name = "l2_core_bound"
    eventinfos.extend([fetch_latency, fetch_bandwidth, branch_mispredicts, machine_clears, memory_bound, core_bound])

    #another first level
    frontend_bound1 = (total_slots - eventsets['dec_val_uops_num']) / total_slots
    bad_speculation1 = (eventsets['dec_fire_uops_num'] - eventsets['insts']) / total_slots
    retire1 = eventsets['insts'] / total_slots
    backend_bound1 = (frontend_bound1 + bad_speculation1 + retire1) * -1.0 + 1.0

    frontend_bound1.name = "t1_frontend_bound1"
    bad_speculation1.name = "t1_bad_speculation1"
    retire1.name = "t1_retire1"
    backend_bound1.name = "t1_backend_bound1"
    eventinfos.extend([frontend_bound1, bad_speculation1, retire1, backend_bound1])




#----------------------------------------------------------------------------------#

if len(sys.argv) < 3: 
    print("parameters are not enough.\n ./process.py events.list logfile respath")
    exit()

eventlist=sys.argv[1]
if not os.path.exists(sys.argv[1]):
    print(sys.argv[1]+" is not exist.")
    exit()

logfile=sys.argv[2]
if not os.path.exists(sys.argv[2]):
    print(sys.argv[2]+" is not exist.")
    exit()

respath=""
(filepath, tempfilename) = os.path.split(logfile)
(filepref, filesuff) = os.path.splitext(tempfilename)
if len(sys.argv) == 3:
    respath = filepath
else:
    if not os.path.exists(sys.argv[3]):
        os.makedirs(sys.argv[3])
    respath = sys.argv[3]

eventdict = read_eventlist(eventlist)
eventinfos, eventsets = readEventInfo(logfile, eventdict)
process_infos(eventinfos, eventsets)

savename = respath + "/" + filepref + "_eventinfo"+".csv"
saveEventInfo(eventinfos, savename)