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
RUN wget http://jjguy.com/heatmap/heatmap-2.2.1.tar.gz && tar xzf heatmap-2.2.1.tar.gz && cd heatmap-2.2.1 && python2 setup.py install

COPY . /root/trackdirect

VOLUME /root/trackdirect/config/trackdirect.ini
VOLUME /root/trackdirect/htdocs/public/heatmaps
