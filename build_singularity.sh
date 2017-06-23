#!/bin/bash

rm scraper.img
singularity create --size 6000 scraper.img
sudo singularity bootstrap scraper.img Singularity
