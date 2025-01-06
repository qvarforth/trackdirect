
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
  python3 \
  python3-dev \
  python3-pip \
  python-is-python3 \
  git \
  wget \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

COPY . /root/trackdirect

COPY .pgpass /root/.pgpass
RUN chmod 600 /root/.pgpass

RUN python3 -m pip config set global.break-system-packages true
RUN pip install -r /root/trackdirect/requirements.txt
