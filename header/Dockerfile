FROM ubuntu:16.04

# docker build -t pydicom/dicom-header-cleaner .

# How to run the image for development (binding code folder to image)
# docker run --entrypoint bash -v $PWD:/code -it pydicom/dicom-header-cleaner

########################################
# Configure
########################################

ENV DISPLAY :99.0
ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive

########################################
# Dependencies
######################################## 

RUN apt-get update && \
    apt-get install -y nginx \
                       git \ 
                       python3-pip \
                       python3-dev \
                       ipython3 \
                       python3-tk \
                       xvfb

RUN python3 -m pip install numpy matplotlib scikit-image deid
RUN python3 -m pip install scikit-learn==0.15.2

WORKDIR /opt
RUN git clone https://www.github.com/pydicom/pydicom
RUN git clone https://www.github.com/pydicom/deid

# Install Pydicom
WORKDIR /opt/pydicom
RUN git checkout affb1cf10c6be2aca311c29ddddc622f8bd1f810 && \
    python3 setup.py install && \
    apt-get clean

########################################
# Content
########################################

RUN mkdir -p /data/input
RUN mkdir -p /data/output/flagged
RUN mkdir -p /data/output/clean

RUN mkdir -p /code  # code
WORKDIR /code
ADD . /code
RUN chmod u+x /code/entrypoint.sh

ENTRYPOINT ["/code/entrypoint.sh"]
