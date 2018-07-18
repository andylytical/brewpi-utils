#!/bin/bash

set -x

USER="andylytical"
IMAGE="brewpi-backup"
TAG=$( date "+%Y%m%d" )
SRCREPO="https://github.com/andylytical/brewpi-utils.git"
SRCDIR="src"


# Ensure latest code
[[ -d $SRCDIR ]] && rm -rf $SRCDIR
(
git clone "$SRCREPO" "$SRCDIR"
cd "$SRCDIR"
git pull
git submodule update --init
git submodule update --recursive --remote
)

# BUILD IMAGE
docker build . -t $IMAGE:$TAG
docker tag $IMAGE:$TAG $USER/$IMAGE:$TAG
#docker push $USER/$IMAGE:$TAG
