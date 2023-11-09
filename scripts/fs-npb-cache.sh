#!/bin/bash
cd $GEM5_ROOT

if [ $# == 0 ]; then
    echo "Please specify checkpoint ID"
    exit 1
fi

./build/X86_MESI_Three_Level/gem5.opt \
\
--debug-flags=Checkpoint \
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
--num-clusters=1 \
--l0d_size=64kB \
--l0d_assoc=2 \
--l0i_size=64kB \
--l0i_assoc=2 \
--l1d_size=1MB \
--l1d_assoc=8 \
--l2_size=1GB \
--l2_assoc=16 \
--cacheline_size=64 \
--ruby \
\
--network=garnet \
--topology=DragonFly4x4_3level \
--num-mems=16 \
--num-cpus=4 \
--num-l2caches=4 \
--num-dir=16 \
--router-latency=4 \
--link-width-bits=512 \

