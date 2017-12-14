FROM python:2.7


RUN mkdir /code
RUN mkdir /data

ENV PATH /opt/anaconda2/bin:$PATH
ENV DISPLAY :99.0
ENV DEBIAN_FRONTEND noninteractive

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
        libjasper-dev \
        libavformat-dev \
        libpq-dev


# Python 2
RUN wget https://repo.continuum.io/archive/Anaconda2-4.4.0-Linux-x86_64.sh
RUN bash Anaconda2-4.4.0-Linux-x86_64.sh -b -p /opt/anaconda2
RUN /opt/anaconda2/bin/conda install numpy
RUN /opt/anaconda2/bin/pip install nolearn
RUN /opt/anaconda2/bin/pip install scikit-learn==0.15.2


# Install Pydicom
WORKDIR /opt
RUN git clone https://www.github.com/pydicom/pydicom
RUN git clone https://www.github.com/pydicom/deid
WORKDIR /opt/pydicom
RUN /opt/anaconda2/bin/python setup.py install
WORKDIR /opt/deid
RUN /opt/anaconda2/bin/python setup.py install

RUN mkdir /code/data
RUN mkdir /code/user
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

ENV LC_ALL C
WORKDIR /code

ENTRYPOINT ["/code/entrypoint.sh"]
