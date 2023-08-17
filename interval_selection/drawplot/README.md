1. draw_cluster_result.py:
    - It is used to draw the hardware events of each interval obtained by hardware sampling as line graphs, and mark the position of the interval specified in the cluster_result.total file
    - Usage：./draw_cluster_result.py sampling_result.csv cluster_res.total respath
        - sampling_result.csv: Hardware event information for each program interval obtained by hardware sampling
        - cluster_res.total: The results obtained after cluster analysis, including the position and weight of the selected program intervals

2. draw_bbv_dis.py:
    - It is used to draw a matrix diagram based on the BBV distance between the specified program intervals.
    - Usage：./draw_bbv_dis.py  bbv_maxtrix.bbv_dis cluster_res.total
        - bbv_maxtrix.bbv_dis: The normalized Manhattan distance of each interval relative to all other intervals calculated from each interval's BBV.
        - cluster_res.total: The results obtained after cluster analysis, including the position and weight of the selected program intervals

3. Requires: matplotlib (Version: 3.5.1)
