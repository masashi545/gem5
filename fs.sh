#!/bin/bash

./build/X86/gem5.opt \
\
--debug-flags=TracePacket \
--debug-file=trace.out \
\
configs/example/fs.py \
\
--kernel=resource/kernels/x86_64-vmlinux-2.6.22.9.smp \
--disk-image=resource/disks/ \
\
--cpu-clock=3.5GHz \
--cpu-type=TimingSimpleCPU \
\
--script=scripts/npb \
\
--caches \
--l2cache \
--ruby \
\
--network=garnet \
--topology=DragonFly4x4 \
--num-cpus=4 \
--num-l2caches=4 \
--num-dir=4 \
--router-latency=4 \
--link-width-bits=512 \
