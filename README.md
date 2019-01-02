# Dicom Cleaner

This repository provides tools intended for use to scrape personal health information (PHI)
that is represented as text from image headers and pixels. Each subfolder here corresponds
to a different kind of cleaner, and a docker container. 

 - [ocr](ocr) "optical character recognititon" is an image that runs text (letter detection) on a demo image. You can either detect (just find and report) or clean the data (and save cleaned png images).
 - [header](header) uses the [deid](https://www.github.com/pydicom/deid) python module to target known coordinates based on manufacturer and machine types to flag images. The coordinates are then cleaned (covered with a black box).

Both containers are available on Docker Hub under the [pydicom organization](https://cloud.docker.com/u/pydicom/repository/list)
