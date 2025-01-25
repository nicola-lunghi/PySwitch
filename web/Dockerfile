FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# UPDATE PACKAGES
RUN apt-get update

# INSTALL SYSTEM UTILITIES
RUN apt-get install -y \
    apt-utils \
    curl \
    vim \
    apt-transport-https \
    software-properties-common

# INSTALL APACHE2
RUN apt-get install -y apache2
RUN a2enmod rewrite

# INSTALL locales
RUN apt-get install -qy language-pack-en-base \
    && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# INSTALL PHP & LIBRARIES
RUN add-apt-repository -y ppa:ondrej/php
RUN apt-get update
RUN apt-get --no-install-recommends --no-install-suggests --yes --quiet install \
    php-pear \
    php8.2 \
    php8.2-common \
    php8.2-mbstring \
    php8.2-dev \
    php8.2-xml \
    php8.2-cli \
    php8.2-mysql \
    php8.2-sqlite3 \
    php8.2-mbstring \
    php8.2-curl \
    php8.2-gd \
    php8.2-imagick \
    php8.2-xdebug \
    php8.2-xml \
    php8.2-zip \
    php8.2-odbc \
    php8.2-opcache \
    php8.2-redis \
    autoconf \
    zlib1g-dev \
    libapache2-mod-php8.2

# INSTALL ODBC DRIVER & TOOLS


# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
# RUN apt-get update
# RUN ACCEPT_EULA=Y apt-get install -y \
#     msodbcsql18 \
#     mssql-tools18 \
#     unixodbc \
#     unixodbc-dev

# RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
# RUN exec bash

# # INSTALL & LOAD SQLSRV DRIVER & PDO
# RUN pecl install sqlsrv
# RUN echo "extension=sqlsrv.so" > /etc/php/8.2/cli/conf.d/20-sqlsrv.ini
# RUN echo "extension=sqlsrv.so" > /etc/php/8.2/apache2/conf.d/20-sqlsrv.ini

# RUN pecl install pdo_sqlsrv
# RUN echo "extension=pdo_sqlsrv.so" > /etc/php/8.2/cli/conf.d/30-pdo_sqlsrv.ini
# RUN echo "extension=pdo_sqlsrv.so" > /etc/php/8.2/apache2/conf.d/30-pdo_sqlsrv.ini

EXPOSE 80

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]