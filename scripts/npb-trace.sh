#!/bin/bash
cd $GEM5_ROOT

# checkpoint_v1
#   EP,5130539321337 1
#   LU,5131105220872 2
#   SP,5132044871280 3
#   IS,5136721304832 4
#   MG,5136780010068 5
#   FT,5139888803829 6
#   BT,5141050100037 7
#   CG,5151547669293 8
app=(ep lu sp is mg ft bt cg)

# checkpoint_v2
#   EP,5007655068597 1
#   SP,5008897387368 2
#   LU,5009138856657 3
#   BT,5010236151931 4
#   IS,5010748286949 5
#   MG,5011146925911 6
#   FT,5013067625622 7
#   CG,5024160137674 8
#app=(ep sp lu bt is mg ft cg)

size=8
topo_size=`expr ${size} \* ${size}`

dir_path=./m5out/trace${size}x${size}
mkdir -p ${dir_path}
mkdir -p "../booksim2/trace${size}x${size}"

for ((i=1; i<4; i++))
do
    echo $i ${app[i-1]}

    ./scripts/fs-npb.sh ${i} ${topo_size} > stdout

    echo "time,src,dest,size,type" > ${dir_path}/${app[i-1]}_trace.csv
    awk 'NR >= 2 {printf "%d,%d,%d,%d,%s\n", $1, $4, $5, $6, $7}' ./m5out/debug.out >> ${dir_path}/${app[i-1]}_trace.csv

    python ./scripts/trace.py ${dir_path}/${app[i-1]}_trace.csv
done