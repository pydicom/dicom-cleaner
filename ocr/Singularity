Bootstrap: docker
From: python:2.7

%files
. /code

%environment
PATH=/opt/anaconda2/bin:$PATH
export PATH

%runscript

export DISPLAY=:99.0
exec xvfb-run /opt/anaconda2/bin/python /code/main.py


%post
DEBIAN_FRONTEND=noninteractive

apt-get update && \
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
wget https://repo.continuum.io/archive/Anaconda2-4.4.0-Linux-x86_64.sh
bash Anaconda2-4.4.0-Linux-x86_64.sh -b -p /opt/anaconda2
/opt/anaconda2/bin/conda install numpy
/opt/anaconda2/bin/pip install nolearn
/opt/anaconda2/bin/pip install scikit-learn==0.15.2

mkdir /data

# Install Pydicom
cd /opt
git clone https://www.github.com/pydicom/pydicom
git clone https://www.github.com/pydicom/deid
cd /opt/pydicom
/opt/anaconda2/bin/python setup.py install
cd /opt/deid
/opt/anaconda2/bin/python setup.py install
cd /opt

if [ ! -d "/data" ]; then
  mkdir /data
fi

if [ ! -d "/code" ]; then
  mkdir /code
fi
