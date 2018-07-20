#!/bin/bash

set -x

# setup pythonpath to include all submodules
parts=( $PYTHONPATH )
for d in submodules/*; do
    parts+=( $( readlink -e $d ) )
done
OIFS="$IFS"
IFS=":"; PYPATH="${parts[*]}"
IFS="$OIFS"
export PYTHONPATH=$PYPATH

python test.py
#python pathdump.py
