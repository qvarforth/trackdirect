
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
  python3 \
  python3-dev \
  python3-pip \
  git \
  curl \
  wget \
  gcc \
  && rm -rf /var/lib/apt/lists/*

COPY . /root/trackdirect

RUN pip install -r /root/trackdirect/requirements.txt
