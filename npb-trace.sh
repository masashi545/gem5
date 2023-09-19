#!/bin/bash

if [ $# != 1 ]; then
    echo "Please select an application from { bt, cg, dc, ep, ft, is, lu, mg, sp, ua }"
    exit 1
fi

./fs-checkpoint.sh $1

./fs-npb.sh 1

rm -r ./m5out/cpt.*

echo "Time,src,dest,size,type" > ./m5out/$1_trace.csv
awk 'NR >= 2 {printf "%d,%d,%d,%d,%s\n", $1, $4, $5, $6, $7}' ./m5out/debug.out >> ./m5out/$1_trace.csv