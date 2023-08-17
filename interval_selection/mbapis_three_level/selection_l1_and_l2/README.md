1. select_tailored_interval.py
    - According to the specified hardware event names and the corresponding priority ratios, find the position of the program intervals that meet the conditions from the hardware sampling results. Our own hardware event names are contained in the events.list file. 
    - Usage：./select_tailored_interval.py sampling_result.csv event1 ratio1 event2 ratio2 (eventn ratio_n)
        - event1 & ratio1：From the sampling_result.csv file, according to the event1, sort all the intervals from high to low, and then select a part of the top intervals according to ratio1 to form the set_l1_event1 set. 
        - event2 & ratio2：From the sampling_result.csv file, according to the event2, sort all the intervals from high to low, and then select a part of the top intervals according to ratio2 to form the set_l2_event2 set.
        - eventn & ratio_n: Optional.
        - The final result is the intersection of set_l1_event1 and set_l2_event2, that is, the set of program intervals that meet the requirements of both the first level and the second level.
    - output
        - bench_event1_ratio1_event2_ratio2.si: the positions of all selected intervals
        - dinfo_bench_event1_ratio1_event2_ratio2.csv：the detailed information of all selected intervals
    - example:
        ```python
            #first level: eventname = com_misp_MPKI, ratio1 = 50%
            #second level: topdownname = l2_branch_mispredicts, ratio2 = 50%
            ./select_tailored_interval.py gcc_eventinfo.csv com_misp_MPKI 0.5 l2_branch_mispredicts 0.5
        ```
