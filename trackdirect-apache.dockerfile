FROM php:7.2-apache

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

RUN pecl install imagick && docker-php-ext-enable imagick && docker-php-ext-install pdo pdo_pgsql

COPY . /root/trackdirect
COPY config/000-default.conf /etc/apache2/sites-enabled/

RUN a2enmod rewrite
RUN chmod a+rx / && chmod a+rx -R /root
RUN chmod 777 /root/trackdirect/htdocs/public/symbols

RUN rm /root/trackdirect/config/trackdirect.ini

VOLUME /root/trackdirect/config/trackdirect.ini
VOLUME /root/trackdirect/htdocs/public/heatmaps
