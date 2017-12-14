#!/usr/bin/bash
scp vsochat@cci-docker-webapp-d01:/home/vsochat/TEST/*.pkl $PWD
mkdir -p $PWD/data/output
mkdir -p $PWD/data/input && cd data/input
scp vsochat@cci-docker-webapp-d01:/home/vsochat/TEST/data/* $PWD
