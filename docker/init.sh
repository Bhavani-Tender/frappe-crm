#!/bin/bash
set -e

if [ -d "/home/frappe/frappe-bench/apps/frappe" ]; then
    echo "Bench already exists."
    cd /home/frappe/frappe-bench
    exec bench start
fi

echo "Creating Frappe Bench..."

cd /home/frappe

bench init --skip-redis-config-generation frappe-bench --version version-15

cd frappe-bench

# Configure services
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Remove Redis processes from Procfile
sed -i '/redis/d' Procfile
sed -i '/watch/d' Procfile

# Allow git to use mounted repository
git config --global --add safe.directory /workspace

# Install CRM app from your mounted repository
bench get-app --soft-link /workspace

# Create site
bench new-site crm.localhost \
    --force \
    --mariadb-root-password 123 \
    --admin-password admin \
    --no-mariadb-socket

# Install CRM
bench --site crm.localhost install-app crm

# Development settings
bench --site crm.localhost set-config developer_mode 1
bench --site crm.localhost set-config mute_emails 1
bench --site crm.localhost set-config server_script_enabled 1

bench use crm.localhost

exec bench start