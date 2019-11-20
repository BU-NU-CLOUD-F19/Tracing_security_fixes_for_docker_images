#!/bin/bash
#########################################################################
# Author: Srinithi Ramesh <ramesh.sr@husky.neu.edu>                     #
#                                                                       #
# Script to pull a docker image's sources, untar and extract the OS and #
# then delete the image (if it is not used by any running container)    #
#                                                                       #
#########################################################################

mkdir image_source
docker export $(docker create $1) | tar -C image_source/ -xvf -
source image_source/etc/os-release
os=$ID
rm -r image_source
docker system prune -af
echo $os
