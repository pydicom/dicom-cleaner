FROM python:2.7

ENV LC_ALL C
ENV PATH /opt/anaconda2/bin:$PATH
ENV DISPLAY :99.0
ENV DEBIAN_FRONTEND noninteractive
ARG PYDICOM_VERSION 1.2.1
ARG DEID_VERSION 0.1.27

RUN apt-get update && \
        apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        xvfb \
        xorg \
        pkg-config \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavformat-dev \
        libpq-dev

# Python 2
RUN wget https://repo.continuum.io/archive/Anaconda2-4.4.0-Linux-x86_64.sh
RUN bash Anaconda2-4.4.0-Linux-x86_64.sh -b -p /opt/anaconda2
RUN /opt/anaconda2/bin/conda install --yes numpy && \
    /opt/anaconda2/bin/pip install nolearn && \
    /opt/anaconda2/bin/pip install scikit-learn==0.15.2 && \
    /opt/anaconda2/bin/pip install deid==${DEID_VERSION} && \
    /opt/anaconda2/bin/conda install --yes -c conda-forge gdcm

# Install Pydicom
WORKDIR /opt
RUN wget https://github.com/pydicom/pydicom/archive/v${PYDICOM_VERSION}.tar.gz && \
    tar xzvf v1.2.1.tar.gz && \
    cd pydicom-${PYDICOM_VERSION} && \
    /opt/anaconda2/bin/python setup.py install

RUN mkdir -p /code/data && \
    mkdir -p /code/user && \
    mkdir -p /data

ADD cifar /code/cifar
ADD data/__init__.py /code/data/__init__.py
ADD main.py /code/main.py
ADD user/__init__.py /code/user/__init__.py
ADD data/linearsvc-hog-fulltrain2-90.pickle /code/data/linearsvc-hog-fulltrain2-90.pickle
ADD data/linearsvc-hog-fulltrain36-90.pickle /code/data/linearsvc-hog-fulltrain36-90.pickle
ADD data/__init__.py /code/data/__init__.py
ADD logger.py /code/logger.py
ADD entrypoint.sh /code/entrypoint.sh
RUN chmod u+x /code/entrypoint.sh

WORKDIR /code

ENTRYPOINT ["/code/entrypoint.sh"]
