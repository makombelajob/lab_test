FROM php:8.4-apache

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    build-essential \
    curl \
    zlib1g-dev \
    libicu-dev \
    zip \
    libzip-dev \
    libpng-dev \
    libjpeg62-turbo-dev \
    libwebp-dev \
    libfreetype6-dev \
    iputils-ping \
 && rm -rf /var/lib/apt/lists/*

# Extensions PHP
RUN docker-php-ext-install mysqli pdo pdo_mysql intl opcache \
 && pecl install apcu \
 && docker-php-ext-enable apcu

RUN docker-php-ext-configure gd --with-freetype --with-webp --with-jpeg \
 && docker-php-ext-install gd

# Apache
RUN a2enmod rewrite socache_shmcb

# Composer
RUN curl -sS https://getcomposer.org/installer | php \
 -- --install-dir=/usr/local/bin --filename=composer

# Symfony CLI
RUN curl -sS https://get.symfony.com/cli/installer | bash \
 && mv /root/.symfony*/bin/symfony /usr/local/bin/symfony

# =========================
# PYTHON VENV (CLÉ DU SUCCÈS)
# =========================
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install \
    mysql-connector-python \
    numpy \
    requests \
    python-dotenv \
    beautifulsoup4 \
    lxml

# Activer le venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/var/www/html:$PYTHONPATH"
WORKDIR /var/www/html
