#!/bin/bash

set -x

USER="andylytical"
IMAGE="brewpi-backup"
TAG=$( date "+%s" )

# BUILD IMAGE
#docker build . -t $IMAGE:$TAG
docker build . -t $IMAGE
#docker tag $IMAGE:$TAG $USER/$IMAGE:$TAG
#docker tag $USER/$IMAGE:$TAG $USER/$IMAGE:latest
#docker push $USER/$IMAGE:$TAG
