FROM php:8.0-apache

RUN apt-get update && apt-get install -y \
  git \
  libpq-dev \
  postgresql-client-common \
  postgresql-client \
  libevent-dev \
  libmagickwand-dev \
  imagemagick \
  inkscape \
  && rm -rf /var/lib/apt/lists/*

RUN pecl install imagick && docker-php-ext-enable imagick && docker-php-ext-install pdo pdo_pgsql && docker-php-ext-install gd && docker-php-ext-enable gd

COPY . /root/trackdirect
COPY config/apache-default.conf /etc/apache2/sites-enabled/000-default.conf

RUN a2enmod rewrite
RUN chmod a+rx / && chmod a+rx -R /root
RUN chmod 777 /root/trackdirect/htdocs/public/symbols
RUN chmod 777 /root/trackdirect/htdocs/public/heatmaps

