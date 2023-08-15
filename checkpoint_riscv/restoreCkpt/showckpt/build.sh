#!/bin/bash

cc=g++
flags="-static -O2"
dflags=""
target="showckpt.x86"

filelist="*.cpp"
echo ${cc} $filelist $flags $dflags -o ${target}
${cc} $filelist $flags $dflags -w -o ${target}

