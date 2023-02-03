#!/bin/bash

COMMON="./build/X86_MOESI_CMP_directory/gem5.opt \
        --debug-flags=TracePacket --debug-file=trace.out \
        configs/example/fs.py \
        --kernel=resource/kernels/x86_64-vmlinux-2.6.22.9.smp \
        --disk-image=resource/disks/linux-x86-npb.img \
        --cpu-clock=3GHz --cpu-type=TimingSimpleCPU --restore-with-cpu=TimingSimpleCPU \
        --caches --l2cache --ruby \
        --l1d_size=32kB --l1i_size=32kB --l2_size=256kB \
        --network=garnet --topology=DragonFly4x4 \
        --num-mem=16 --num-cpus=4 --num-l2caches=4 --num-dir=4 \
        --router-latency=4 --link-width-bits=512"

app=(ep sp is lu mg bt ft ua cg dc)

for ((i=1; i<11; i++))
do
  $COMMON --checkpoint-restore=$i
  cp ./m5out/stats.txt ./data/${app[i-1]}_stats.txt
done
