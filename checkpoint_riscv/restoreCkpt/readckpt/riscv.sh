#!/bin/bash

cc=riscv64-unknown-linux-gnu-g++
flags="-static -O2"
target="readckpt_gen.riscv"

filelist=`find . -name "*.cpp" `
echo ${cc} $filelist $flags -T ./link.lds -o ${target}
${cc} $filelist $flags -T ./link.lds -o ${target}

# objdump=riscv64-unknown-linux-gnu-objdump
# echo ${objdump} -d ${target} 
# ${objdump} -d ${target} >read.s
