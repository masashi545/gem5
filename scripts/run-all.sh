#!/bin/bash

for app in bt cg dc ep ft is lu mg sp ua
do
    echo "running .. ${app}"
    ./scripts/npb-trace.sh ${app}
done
