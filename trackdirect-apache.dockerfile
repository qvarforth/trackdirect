FROM php:8.2-apache

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

RUN mkdir -p /var/cache/apache2/mod_cache_disk/trackdirect/
RUN chown -R www-data:www-data /var/cache/apache2/mod_cache_disk
RUN a2enmod rewrite
RUN a2enmod cache
RUN a2enmod cache_disk
RUN chown -R www-data:www-data /root

