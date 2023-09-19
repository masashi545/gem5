#!/bin/bash

if [ $# == 0 ]; then
    echo "Please specify checkpoint ID"
    exit 1
fi

./build/X86/gem5.opt \
\
--debug-flags=TracePacket \
--debug-file=debug.out \
\
configs/example/fs.py \
\
--kernel=resource/kernels/x86_64-vmlinux-2.6.22.9.smp \
--disk-image=resource/disks/linux-x86-npb.img \
\
--cpu-clock=3GHz \
--cpu-type=TimingSimpleCPU \
\
--checkpoint-restore=$1 \
--restore-with-cpu=TimingSimpleCPU \
\
--mem-size=8GB \
--caches \
--l2cache \
--l1d_size=32kB \
--l1i_size=32kB \
--l2_size=256kB \
--ruby \
\
--network=garnet \
--topology=Mesh_XY \
--num-mems=16 \
--num-cpus=4 \
--num-l2caches=4 \
--num-dir=16