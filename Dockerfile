FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    git \
    postgresql-client \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    node-less \
    && rm -rf /var/lib/apt/lists/*

# Create odoo user
RUN useradd -ms /bin/bash odoo

# Set work directory
WORKDIR /opt/odoo

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Odoo source code
COPY . .

# Copy custom addons
RUN mkdir -p /opt/odoo/custom_addons
COPY odoo/Custom_addons /opt/odoo/custom_addons/

# Set permissions
RUN chown -R odoo:odoo /opt/odoo

# Switch to odoo user
USER odoo

# Expose port
EXPOSE $PORT

# Start command
CMD ["python3", "odoo-bin", "-c", "odoo.conf"]
