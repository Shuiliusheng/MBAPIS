## MBAPIS: Multi-Level Behavior Analysis Guided Program Interval Selection for Microarchitecture Studies

> Multi-level Behavior Analysis guided Program Interval Selection (MBAPIS) is used to select tailored intervals. For a given microarchitecture study, the frst level of MBAPIS uses hardware performance counters to prioritize selecting the intervals that exhibit clearer microarchitectural characteristics relevant to that study. The second level analyzes the processor performance bottlenecks to further select the intervals where the concerned microarchitecture design more strongly impacts performance. Finally, MBAPIS performs clustering analysis with the basic block information of each interval selected by the frst two levels, and selects the representative intervals among them while preserving the diverse software behavior. Additionally, we present a general and extensible interval-replaying design to accurately re-execute selected intervals. (MBAPIS is presetend at PACT 2023.)

## About The Directory
1. interval_selection: We can select representative tailored intervals from the target program by specifying specific hardware events and TopDown performance bottleneck metrics, using the provided scripts in this directory.

2. checkpoint_riscv: This directory provides the modified gem5 to create checkpoints for desired program intervals and the checkpoint loader to read these checkpoints and replay intervals.
