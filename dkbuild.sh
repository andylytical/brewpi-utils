#!/bin/bash

USER=andylytical
TS=$( date +%s )

fatal() {
    echo "Error: $*"
    exit 1
}

[[ $# -eq 1 ]] || fatal "expected 1 argument, got '$#'"
[[ -d "$1" ]] || fatal "not a directory: '$1'"
NAME="$1"

set -x

docker build \
    -f $NAME/Dockerfile \
    -t $NAME \
    -t $USER/$NAME:$TS \
    -t $USER/$NAME:latest \
    .

docker push $USER/$NAME:$TS
