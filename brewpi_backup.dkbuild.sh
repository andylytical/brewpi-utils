#!/bin/bash

set -x


NAME=brewpi-backup
USER=andylytical
TS=$( date +%s )

docker build \
    -f $NAME/Dockerfile \
    -t $NAME \
    -t $USER/$NAME:$TS \
    -t $USER/$NAME:latest \
    .

docker push $USER/$NAME:$TS
