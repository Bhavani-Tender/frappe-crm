#!/bin/bash
set -e

BENCH_DIR="/home/frappe/frappe-bench"
SITE_NAME="crm.localhost"

# Bench already exists
if [ -d "$BENCH_DIR/apps/frappe" ]; then
    echo "Bench already exists."

    cd $BENCH_DIR

    if [ -d "$BENCH_DIR/sites/$SITE_NAME" ]; then
        echo "Site already exists."
    else
        echo "Creating site..."

        bench new-site $SITE_NAME \
            --force \
            --mariadb-root-password 123 \
            --admin-password admin \
            --no-mariadb-socket

        bench --site $SITE_NAME install-app crm

        bench --site $SITE_NAME set-config developer_mode 1
        bench --site $SITE_NAME set-config mute_emails 1
        bench --site $SITE_NAME set-config server_script_enabled 1

        bench use $SITE_NAME
    fi

    exec bench start
fi

echo "Creating Frappe Bench..."

cd /home/frappe

bench init --skip-redis-config-generation frappe-bench --version version-15

cd frappe-bench

bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

sed -i '/redis/d' Procfile
sed -i '/watch/d' Procfile

git config --global --add safe.directory /workspace

bench get-app --soft-link /workspace

bench new-site $SITE_NAME \
    --force \
    --mariadb-root-password 123 \
    --admin-password admin \
    --no-mariadb-socket

bench --site $SITE_NAME install-app crm

bench --site $SITE_NAME set-config developer_mode 1
bench --site $SITE_NAME set-config mute_emails 1
bench --site $SITE_NAME set-config server_script_enabled 1

bench use $SITE_NAME

exec bench start