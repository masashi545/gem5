#!/bin/bash
cd $GEM5_ROOT

#app=(is ep cg mg ft bt sp lu ua dc)
app=(is ep cg mg ft bt sp lu)

echo "checkpoint list" > ./data/cpt-info.txt

for app in ${app[@]}
do
  echo -n "$app," | tr '[:lower:]' '[:upper:]' >> ./data/cpt-info.txt
  ./scripts/fs-checkpoint.sh $app >& stdout
  grep -A 1 "Writing checkpoint" stdout | awk 'NR==2 {printf "%d\n", $7}' >> ./data/cpt-info.txt
done
