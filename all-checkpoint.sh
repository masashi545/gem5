#!/bin/bash

COMMON="./build/X86/gem5.opt configs/example/fs.py \
        --kernel=resource/kernels/x86_64-vmlinux-2.6.22.9.smp \
        --disk-image=resource/disks/linux-x86-npb.img \
        --cpu-clock=3GHz --cpu-type=AtomicSimpleCPU \
        --caches --l2cache --l1d_size=32kB --l1i_size=32kB --l2_size=256kB \
        --num-cpus=4 --num-dir=4"

app=(is ep cg mg ft bt sp lu ua dc)

for app in ${app[@]}
do
  echo "START: $app"
  $COMMON --script=scripts/npb/$app.sh >& std.out
  grep -A 1 -n "Writing checkpoint" std.out
  echo "FINISH: $appi \n"
done
