#!/bin/bash
# Get the TAG from first parameter, if not ask (and default get the git branch)
if [ ! -z $1 ]; then
    export TAG=$1
else
    CURRENT_BRANCH=$(git rev-parse --symbolic-full-name --abbrev-ref HEAD)
    read -e -p "Please, enter TAG to deploy [$CURRENT_BRANCH]: " TAG
    export TAG="${TAG:-${CURRENT_BRANCH}}"
fi

rm -rf exo-backoffice/*

docker run --name $TAG exolever/exo-backoffice:$TAG
docker cp $TAG:/projects/service-exo-core/exo-backoffice/ .
docker rm $TAG
docker image rm exolever/exo-backoffice:$TAG
