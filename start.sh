#!/bin/bash

# Wait for database to be ready
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Waiting for database..."
  sleep 2
done

# Initialize database if it doesn't exist
python3 odoo-bin -c odoo.conf -d $DB_NAME --init=base --stop-after-init

# Install your custom module
python3 odoo-bin -c odoo.conf -d $DB_NAME -i app1 --stop-after-init

# Start Odoo
exec python3 odoo-bin -c odoo.conf
