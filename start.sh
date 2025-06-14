#!/bin/bash

# Parse DATABASE_URL if provided
if [ ! -z "$DATABASE_URL" ]; then
    # Extract components from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
    DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*\/\/[^:]*:\([^@]*\)@.*/\1/p')
    
    export DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD
fi

# Set default admin password if not provided
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}

# Start Odoo
python3 odoo/odoo-bin -c odoo.conf