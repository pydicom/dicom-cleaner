# Dicom Scraper (Header)

This Docker image uses deid to flag images, and then replace areas of PHI with black pixels. We use xvfb-run from package xvfb to handle not having a display.

## Docker
First, to build the image:

```
docker build -t vanessa/dicom-cleaner .
```

Then to run it, you can first see if it works:

```
docker run vanessa/dicom-cleaner --help
```

and you should see usage


## Usage
