#!/usr/bin/env bash

sudo docker stop $(docker ps -aq) 

sudo docker rmi $(docker images -q)

