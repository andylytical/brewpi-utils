#!/bin/bash

# setup pythonpath to include all submodules
parts=( $PYTHONPATH )
for d in submodules/*; do
    parts+=( $( readlink -e $d ) )
done
OIFS="$IFS"
IFS=":"; PYPATH="${parts[*]}"
IFS="$OIFS"

python test.py
