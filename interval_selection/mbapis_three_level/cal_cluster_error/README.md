1. cal_cluster_error.py： used to calculate the estimated error for each hardware event caused by cluster analysis
    - Usage: ./cal_cluster_error.py events.list sampling_result.csv cluster_result.total (baseline_intevals.label)
        - events.list: A list of hardware events for which clustering errors need to be compared
        - sampling_result.csv: A csv file that contain all hardware events values for each program interval collected with hardware sampling
        - cluster_result.total: The results obtained through cluster analysis, including the selected interval positions and corresponding weights
        - baseline_intevals.label: The collection of all program interval used by the cluster analysis. If not specified, it means that the cluster analysis is for all program intervals.
    - Output：
        - A csv file containing estimated errors for all hardware events specified

2. Usage examples:
    ```python
        #calculate the estimated error of Simpoint for each hardware event contained in events.list
        python3 compare_cluster_error.py events.list ../logfile/sample_log/gcc_eventinfo.csv ../result/simpoint_bbv/total/gcc_simpoint.total
    ```
    

