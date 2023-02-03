#!/bin/bash

if [ $# != 1 ]; then
    echo "Please select an application from { bt, cg, dc, ep, ft, is, lu, mg, sp, ua }"
    exit 1
fi

./build/X86/gem5.opt \
\
configs/example/fs.py \
\
--kernel=resource/kernels/x86_64-vmlinux-2.6.22.9.smp \
--disk-image=resource/disks/linux-x86-npb.img \
\
--cpu-clock=3GHz \
--cpu-type=AtomicSimpleCPU \
\
--script=scripts/npb/$1.sh \
\
--caches \
--l2cache \
--l1d_size=32kB \
--l1i_size=32kB \
--l2_size=256kB \
\
--num-cpus=4 \
--num-dir=4 \
