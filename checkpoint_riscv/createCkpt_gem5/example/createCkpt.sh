#!/bin/bash

bench=gcc.riscv
settings="settings_pk"
options="166.i -o 166.s"
input=""

#for riscv-pk setting: stack = 0x74000000, mmap = 0x30000000

gem5_dir=/home/###/gem5
$gem5_dir/build/RISCV/gem5.fast $gem5_dir/configs/example/se.py --cpu-type=NonCachingSimpleCPU --mem-type=SimpleMemory --mem-size=8GB --ckptsetting=$settings -c $bench --options="$options" --input="$input"
