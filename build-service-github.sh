#!/bin/bash

set -e

export SERVICE_NAME=$1
export SOURCE_BRANCH=$TRAVIS_BRANCH
export SOURCE_TAG=$TRAVIS_TAG
export SOURCE_NAME=$(echo $SOURCE_BRANCH$SOURCE_TAG | sed "s/\//_/g")
export IMAGE_NAME=exolever/$SERVICE_NAME:$SOURCE_NAME
docker build \
--tag $IMAGE_NAME \
--build-arg AWS_KEY=$AWS_KEY \
--build-arg AWS_SECRET=$AWS_SECRET \
--build-arg SERVICE_NAME=$SERVICE_NAME \
--build-arg SOURCE_NAME=$SOURCE_NAME \
--build-arg SOURCE_TAG=$SOURCE_TAG \
--build-arg SOURCE_BRANCH=$SOURCE_BRANCH \
$SERVICE_NAME/

echo "Running tests..."
docker build \
--file $SERVICE_NAME/Dockerfile.test \
--build-arg SOURCE_NAME=$SOURCE_NAME \
--build-arg AWS_KEY=$AWS_KEY \
--build-arg AWS_SECRET=$AWS_SECRET \
$SERVICE_NAME/

echo "Pushing image..."
echo $DOCKER_HUB_PASSWORD | docker login --username $DOCKER_HUB_USERNAME --password-stdin
docker push $IMAGE_NAME
