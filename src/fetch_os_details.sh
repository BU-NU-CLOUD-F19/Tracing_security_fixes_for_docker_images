#!/bin/bash

mkdir image_source
docker export $(docker create $1) | tar -C image_source/ -xvf -
source image_source/etc/*-release
os=$ID
rm -r image_source
echo $os