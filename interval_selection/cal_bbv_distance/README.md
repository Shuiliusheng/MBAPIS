1. cal_bbv_distance.py
    - 用于根据程序片段的BBV计算每一个片段和其它片段之间的曼哈顿距离。计算得到的矩阵在进行归一化后保存到文件中。
    - Usage: ./cal_bbv_distance.py bench.bbv
        - bench.bbv: 程序每个片段的bbv组成的文件
    - Example: ./cal_bbv_distance.py ../logfile/bbv/gcc_400B_200M.bb