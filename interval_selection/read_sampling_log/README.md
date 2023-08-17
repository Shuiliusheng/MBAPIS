1. It is used to read all hardware events from the sampling result file, and obtain some new values through calculation, such as the ratio and other hardware events, and finally save all data to a csv file.

2. Usage：./process.py logfile result_path
    - logfile: Hardware event data for each program interval collected with hardware sampling
    - result_path：The directory of the result csv file, if not specified, the directory of the logfile file is used