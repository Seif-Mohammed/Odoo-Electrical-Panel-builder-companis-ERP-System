FROM python:3.11-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libtiff5-dev \
    tk-dev \
    tcl-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf
RUN curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && apt-get update \
    && apt-get install -y ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# Create odoo user
RUN useradd --create-home --home-dir /opt/odoo --no-log-init odoo

# Set working directory
WORKDIR /opt/odoo

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy entire project
COPY . .

# Create necessary directories
RUN mkdir -p /var/lib/odoo /var/log/odoo

# Set permissions
RUN chown -R odoo:odoo /opt/odoo /var/lib/odoo /var/log/odoo

# Switch to odoo user
USER odoo

# Expose port
EXPOSE 8069

# Start command
CMD ["python3", "odoo-bin", "--config=/opt/odoo/odoo.conf"]
