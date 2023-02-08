#!/bin/bash

if [ $# != 1 ]; then
    echo "Please specify checkpoint ID"
    exit 1
fi

./build/X86_MOESI_CMP_directory/gem5.opt \
\
--debug-flags=TracePacket \
--debug-file=trace.out \
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
--mem-type=HMC_2500_1x32 \
--caches \
--l2cache \
--l1d_size=32kB \
--l1i_size=32kB \
--l2_size=256kB \
--ruby \
\
--network=garnet \
--topology=DragonFly4x4 \
--num-mem=16 \
--num-cpus=4 \
--num-l2caches=4 \
--num-dir=4 \
--router-latency=4 \
--link-width-bits=512 \
