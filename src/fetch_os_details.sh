#!/bin/bash

mkdir image_source
docker export $(docker create $1) | tar -C image_source/ -xvf -
for file in image_source/etc/*-release; do source $file; done
os=$ID
rm -r image_source
echo $os