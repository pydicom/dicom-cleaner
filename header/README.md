# Dicom Scraper (Header)

This Docker image uses deid to flag images, and then replace areas of PHI with black pixels. We use xvfb-run from package xvfb to handle not having a display.

[![asciicast](https://asciinema.org/a/152540.png)](https://asciinema.org/a/152540)

The Docker image is served [here](https://hub.docker.com/r/vanessa/dicom-scraper/) under the header tag.

## Development

### Build
If you want to build the image locally, do the following. If the image is already provided on Docker Hub, you don't need to do this.

```
docker build -t vanessa/dicom-cleaner .
```

If you need to rebuild and be sure that a cache isn't use, don't forget to add `--no-cache`

```
docker build --no-cache -t vanessa/dicom-cleaner .
```

If you use the image from docker hub, the full uri is `vanessa/dicom-scraper:header`

### Interaction
If you want to interact with the contents of the container, you can do that easily by shelling in and defining the entrypoint to be `/bin/bash`. For easier development (meaning changes on the host change in the container) you can map the present working directory to `/code`.

```
docker run -v $PWD:/code --entrypoint /bin/bash -it vanessa/dicom-scraper:header
```

### Preparation
We will walk through an example below, and if you want to try the container for yourself you will need to dump a bunch of dicom files in a `test/data` folder here. You can see the scripts in [test](test) for how I generated and then transferred my test set - it's basically a random selection of images on the server.  To summarize what our local data looks like:

```
tree -L 1 test/data/
test/data/             # maps to /data in container
├── input
└── output
```


### Run

We run the container user `docker run`. If we tried to run it without an argument, it would call [main.py](main.py) and yell at us for not having an input folder with files.

```
$ docker run vanessa/dicom-cleaner
ERROR Please provide a folder with dicom files with --input.
```

It's more appropriate to ask for `--help` to see usage

```
docker run vanessa/dicom-cleaner --help

usage: main.py [-h] [--input FOLDER] [--outfolder OUTFOLDER]
               [--save [{png,dicom,pdf}]] [--detect] [--deid DEID]

Deid (de-identification) based on header tool.

optional arguments:
  -h, --help            show this help message and exit
  --input FOLDER, -i FOLDER
                        input folder to search for images.
  --outfolder OUTFOLDER, -o OUTFOLDER
                        full path to save output, will use /data/output folder
                        if not specified
  --save [{png,dicom,pdf}]
                        save as png, dicom, or, pdf (default: pdf)
  --detect, -d          Only detect, but don't try to scrub
  --deid DEID           deid recipe, if don't want default
```

The usage suggests the following:

 - we can specify what output format we want saved with `--save`. a PDF report is good for generating in a cluster environment, png are another option that (in the future) can be used to generate a web report. Dicom is what we could eventually use if this were a production tool.
 - `--deid` is the de-identification recipe. The above will use the default provided by deid, and if we need to test, we can customize it here.
 - we need to provide an `--input` folder of dicom files to parse. Remember that this folder has to be inside the container, meaning that we will bind it to a folder in the container.
 - Equivalently, `--outfolder` is where output will be written.


### Usage
Let's first try to run the cleaning procedure to produce each of the different file types.  In the command below, by not specifying `--outfolder` we use the default `/data`, and by not specifying `--save` we use the default of pdf. A json file is also produced with more metadata about reasons for flagging, and lists images are associated with. For example, if an image is flagged for a list we called "whitelist" we would want to pass it through no matter what, and an image flagged with "blacklist" might be quarantined no matted what. The concept of "flagged" just means matching a list.

```
docker run -v $PWD/test/data:/data vanessa/dicom-cleaner --input /data/input
```

You'll see a long print as the images are being processed, finishing with writing an output pdf and json file

```
Found 102 valid dicom files
Processing [images]102 [output-folder]/data
Scrubbing test/data/input/dicom-test-67.dcm.
flagged: dicom-test-67.dcm
Scrubbing test/data/input/dicom-test-56.dcm.
flagged: dicom-test-56.dcm
Scrubbing test/data/input/dicom-test-30.dcm.
flagged: dicom-test-30.dcm
Scrubbing test/data/input/dicom-test-40.dcm.
flagged: dicom-test-40.dcm

...

Scrubbing test/data/input/dicom-test-91.dcm.
flagged: dicom-test-91.dcm
Scrubbing test/data/input/dicom-test-38.dcm.
flagged: dicom-test-38.dcm
json data written to deid-clean-102.json
pdf report written to deid-clean-102.pdf

```

You can also customize the output format to be png images or dicom, respectively:

```
docker run -v $PWD/test/data:/data vanessa/dicom-cleaner --input /data/input --save png
docker run -v $PWD/test/data:/data vanessa/dicom-cleaner --input /data/input --save dicom
```

If you want to test a different deid recipe, just give the full path (which must be mapped to the container) to it:

```
docker run -v $PWD/test/data:/data vanessa/dicom-cleaner --input /data/input --deid /data/deid.custom
```

## Improvements
We will likely modify the image to have an interactive mode, meaning that a web browser will opening to perform the filter. The web browser approach will be nicer in that we can put more information about the flagged groups and reasons on a single page.
