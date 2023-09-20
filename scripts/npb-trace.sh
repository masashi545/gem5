#!/bin/bash
cd $GEM5_ROOT

if [ $# != 1 ]; then
    echo "Please select an application from { bt, cg, dc, ep, ft, is, lu, mg, sp, ua }"
    exit 1
fi

./scripts/fs-checkpoint.sh $1

./scripts/fs-npb.sh 1

#rm -r ./m5out/cpt.*

awk 'NR >= 2 {printf "%d,%d,%d,%d,%s\n", $1, $4, $5, $6, $7}' ./m5out/debug.out >> ./m5out/trace/$1_trace.csv