#!/bin/bash

if [ $# == 0 ]; then
    echo "Please specify checkpoint ID"
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
--cpu-type=TimingSimpleCPU \
\
--checkpoint-restore=$1 \
--restore-with-cpu=TimingSimpleCPU \
\
--mem-type=HMC_2500_1x32 \
--mem-size=8GB \
--caches \
--l2cache \
--l1d_size=32kB \
--l1d_assoc=2 \
--l1i_size=32kB \
--l1i_assoc=2 \
--l2_size=256kB \
--l2_assoc=8 \
--cacheline_size=64 \
--ruby \
\
--network=garnet \
--topology=DragonFly4x4 \
--num-mems=16 \
--num-cpus=4 \
--num-l2caches=4 \
--num-dir=16 \
--router-latency=4 \
--link-width-bits=512 \

