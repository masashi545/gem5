#!/bin/bash
cd $GEM5_ROOT

# Sorted by checkpoint ID
app=(ep lu sp is mg bt ft cg)

for ((i=1; i<9; i++))
do
  ./scripts/fs-npb.sh $i
  cp ./m5out/stats.txt ./data/${app[i-1]}_stats.txt
done

./scripts/all-stats.sh
