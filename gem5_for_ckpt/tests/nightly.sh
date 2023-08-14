#!/bin/bash

# Copyright (c) 2021 The Regents of the University of California
# All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

set -e
set -x

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
gem5_root="${dir}/.."

# We assume the lone argument is the number of threads. If no argument is
# given we default to one.
threads=1
if [[ $# -gt 0 ]]; then
    threads=$1
fi

build_target () {
    isa=$1

    # Try to build. If not, delete the build directory and try again.
    # SCons is not perfect, and occasionally does not catch a necessary
    # compilation: https://gem5.atlassian.net/browse/GEM5-753
    docker run -u $UID:$GID --volume "${gem5_root}":"${gem5_root}" -w \
        "${gem5_root}" --rm gcr.io/gem5-test/ubuntu-20.04_all-dependencies \
            bash -c "scons build/${isa}/gem5.opt -j${threads} \
                || (rm -rf build && scons build/${isa}/gem5.opt -j${threads})"
}

unit_test () {
    build=$1

    docker run -u $UID:$GID --volume "${gem5_root}":"${gem5_root}" -w \
        "${gem5_root}" --rm gcr.io/gem5-test/ubuntu-20.04_all-dependencies \
            scons build/NULL/unittests.${build} -j${threads}
}

# Ensure we have the latest docker images.
docker pull gcr.io/gem5-test/ubuntu-20.04_all-dependencies

# Try to build the ISA targets.
build_target NULL
build_target RISCV
build_target X86
build_target ARM
build_target SPARC
build_target MIPS
build_target POWER

# Run the unit tests.
unit_test opt
unit_test debug
unit_test perf
unit_test prof

# Run the gem5 long tests.
docker run -u $UID:$GID --volume "${gem5_root}":"${gem5_root}" -w \
    "${gem5_root}"/tests --rm gcr.io/gem5-test/ubuntu-20.04_all-dependencies \
        ./main.py run --length long -j${threads} -t${threads}