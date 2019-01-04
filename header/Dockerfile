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
ARG PYDICOM_VERSION=1.2.1
ARG DEID_VERSION=0.1.29

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
                       libgdcm2-dev \
                       libgdcm-cil \
                       libgdcm-tools \
                       python-gdcm \
                       xvfb

RUN python3 -m pip install pip --upgrade && \
    python3 -m pip install numpy matplotlib && \
    python3 -m pip install deid==${DEID_VERSION} && \           
    python3 -m pip install scikit-image && \
    python3 -m pip install scikit-learn==0.15.2 && \
    python3 -m pip install pydicom==${PYDICOM_VERSION}

########################################
# Content
########################################

RUN mkdir -p /data/input
RUN mkdir -p /data/output/flagged
RUN mkdir -p /data/output/clean

RUN mkdir -p /code  # code
WORKDIR /code
ADD . /code
RUN chmod u+x /code/entrypoint.sh && \
    apt-get clean

ENTRYPOINT ["/code/entrypoint.sh"]
