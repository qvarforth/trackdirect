FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
  python2 \
  python2-dev \
  git \
  curl \
  wget \
  gcc \
  && rm -rf /var/lib/apt/lists/*

RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py && python2 get-pip.py
RUN pip2 install psycopg2-binary autobahn[twisted] twisted pympler image_slicer jsmin psutil

RUN git clone https://github.com/rossengeorgiev/aprs-python && cd aprs-python && pip2 install .

COPY . /root/trackdirect

