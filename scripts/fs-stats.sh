#!/bin/bash
cd $GEM5_ROOT

if [ -e $1 ]; then
  cat $1 | grep hostSeconds | awk 'NR==1 {printf "%d ", $2}'
  cat $1 | grep numCycles | awk 'NR==1,NR==4 {sum+=$2} END {printf "%d ", sum}'
  cat $1 | grep simOps | awk 'NR==1 {printf "%d\n", $2}'
else 
  echo "No stats file"
fi
