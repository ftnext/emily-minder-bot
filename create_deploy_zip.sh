#!/bin/bash
set -eu

DOCKER_IMAGE_FOR_BUILD=aws-lambda-python37
DOCKER_IMAGE_VERSION=1.1
DOCKER_IMAGE=$DOCKER_IMAGE_FOR_BUILD:$DOCKER_IMAGE_VERSION

BUILD_DIR=build

rm -rf $BUILD_DIR
mkdir $BUILD_DIR
cp main.py $BUILD_DIR/
cp amazon_env/* $BUILD_DIR/
cp $CREDENTIALS_PATH $BUILD_DIR/

cd $BUILD_DIR
docker build -t $DOCKER_IMAGE .
docker run --rm -v $PWD:/var/task $DOCKER_IMAGE
