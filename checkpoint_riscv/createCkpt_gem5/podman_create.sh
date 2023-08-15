#!/bin/bash
local_gem5_dir=/home/cuihongwei/server20/mbapis/checkpoint_riscv/createCkpt_gem5
build_map="-v ${local_gem5_dir}/build:/home/gem5_src/gem5/build"
src_map="-v ${local_gem5_dir}/src:/home/gem5_src/gem5/src"
config_map="-v ${local_gem5_dir}/configs:/home/gem5_src/gem5/configs"
shell_map="-v ${local_gem5_dir}/example:/home/gem5_src/gem5/example"

map=$build_map" "$src_map" "$config_map" "$shell_map
podman run -it --rm $map $local_dir_map $temp_map registry.cn-hangzhou.aliyuncs.com/ronglonely/gem5:3.0 /bin/bash
