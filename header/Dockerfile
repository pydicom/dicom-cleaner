FROM ubuntu:16.04

# How to build the image, and push to Docker Hub
# docker build -t vanessa/dicom-cleaner .
# docker tag vanessa/dicom-cleaner vanessa/dicom-cleaner:header
# docker push vanessa/dicom-cleaner:header

# How to run the image for development (binding code folder to image)
# docker run --entrypoint bash -v $PWD:/code -it vanessa/dicom-cleaner 

########################################
# Configure
########################################

ENV DISPLAY :99.0
ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive

########################################
# Dependencies
######################################## 

RUN apt-get update && apt-get install -y nginx git python3-pip python3-dev ipython3 python3-tk xvfb
RUN python3 -m pip install numpy matplotlib scikit-image
RUN python3 -m pip install scikit-learn==0.15.2

WORKDIR /opt
RUN git clone https://www.github.com/pydicom/pydicom
RUN git clone -b pixel-cleaning https://www.github.com/pydicom/deid

# Install Pydicom
WORKDIR /opt/pydicom
RUN git checkout affb1cf10c6be2aca311c29ddddc622f8bd1f810
RUN python3 setup.py install

# Install deid
WORKDIR /opt/deid
RUN python3 setup.py install
RUN apt-get clean

########################################
# Content
########################################

RUN mkdir /data  # output content, map here
RUN mkdir /data/flagged
RUN mkdir /data/clean

RUN mkdir /code  # code
WORKDIR /code
ADD . /code
RUN chmod u+x /code/entrypoint.sh

ENTRYPOINT ["/code/entrypoint.sh"]
