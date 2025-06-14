FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    libevent-dev \
    libsasl2-dev \
    libldap2-dev \
    libpq-dev \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libwebp-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /odoo

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Odoo files
COPY . .

# Create odoo user
RUN useradd -ms /bin/bash odoo
RUN chown -R odoo:odoo /odoo

# Switch to odoo user
USER odoo

# Expose port
EXPOSE 8069

# Start command
CMD ["python3", "odoo-bin", "-c", "odoo.conf"]
