# Dicom Scraper

This is currently under development, and builds a Singularity image to run text (letter detection) on a demo image. If this is a route we want to go, this can be tweaked to accept a dicom file, and have some logic for finding and removing classified regions.


## Singularity
A build script is provided that (first removes any existing image) and then builds as follows:

```
singularity create --size 6000 scraper.img
sudo singularity bootstrap scraper.img Singularity
```

Complete credit for the base work goes to [@FraPochetti](http://francescopochetti.com/portfoliodata-science-machine-learning/), I just wrapped the functions in a container, added xvfb and other dependencies to (hopefully) reproduce most of the versions that he used, and then added functions to save to file.


## Example Output
Right now, we are focused on just finding text. I found a random online image of a dicom file with a bunch of text, and went through different steps. First, here are all the Objects, detected on the image (note this is a a random image with text I found on Google):

![lao-detect.png](img/lao-detect.png)


### Objects
And here they are extracted from the image. Note that some of these aren't letters but just blocks with lines:

![lao-detect-check.png](img/lao-detect-check.png)


### Single Character Recognition

We don't really care about this one, it's an attempt to say what letter is what.

![lao-detect-letters.png](img/lao-detect-letters.png)


### Text that Would be Removed
This is the part that (I think) we care about, this is a crappy plot of showing which text would be removed. I think we can ignore the purple region, for our purposes, we would remove all the text found in the image.

![lao-text.png](img/lao-text.png)


For all of the above, this would need some careful work to tweak and test with dicom, and add a step to black out text, and then do test runs with different kinds of burnt text and see what happens.
