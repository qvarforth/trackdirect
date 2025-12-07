FROM php:8.4.8-apache

RUN apt-get update && apt-get install -y \
  git \
  libpq-dev \
  postgresql-client-common \
  postgresql-client \
  libevent-dev \
  libmagickwand-dev \
  imagemagick \
  inkscape \
  fontconfig \
  fonts-dejavu-core \
  libpangocairo-1.0-0 \
  libfreetype6 \
  libxrender1 \ 
  && rm -rf /var/lib/apt/lists/*

RUN pecl install imagick && docker-php-ext-enable imagick && docker-php-ext-install pdo pdo_pgsql && docker-php-ext-install gd && docker-php-ext-enable gd

COPY . /root/trackdirect
COPY config/apache-default.conf /etc/apache2/sites-enabled/000-default.conf

RUN mkdir -p /var/www/.cache/fontconfig && chown -R www-data:www-data /var/www/.cache/fontconfig && chmod -R 777 /var/www/.cache/fontconfig
RUN mkdir -p /var/www/.config/inkscape && chown -R www-data:www-data /var/www/.config && chmod -R 777 /var/www/.config/inkscape
RUN mkdir -p /var/cache/apache2/mod_cache_disk/trackdirect && chown -R www-data:www-data /var/cache/apache2/mod_cache_disk

ENV HOME=/var/www
ENV FONTCONFIG_PATH=/etc/fonts
ENV FONTCONFIG_CACHE=$HOME/.cache/fontconfig
ENV XDG_CACHE_HOME=$HOME/.cache/fontconfig
ENV DISPLAY=none

RUN a2enmod rewrite
RUN a2enmod cache
RUN a2enmod cache_disk
RUN chown -R www-data:www-data /root
USER www-data
