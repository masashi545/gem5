#!/bin/bash
cd $GEM5_ROOT

echo "simTime,numCycles,numOps" > data/all-stats.csv

app=(is ep cg mg ft bt sp lu)

for app in ${app[@]}
do
  if [ -e data/$app\_stats.txt ]; then
    cat data/$app\_stats.txt | grep hostSeconds | awk 'NR==1 {printf "%d,", $2}' >> data/all-stats.csv
    cat data/$app\_stats.txt | grep numCycles | awk 'NR==1,NR==4 {sum+=$2} END {printf "%d,", sum}' >> data/all-stats.csv
    cat data/$app\_stats.txt | grep simOps | awk 'NR==1 {printf "%d\n", $2}' >> data/all-stats.csv
  else
    echo ",," >> data/all-stats.csv
  fi
done
