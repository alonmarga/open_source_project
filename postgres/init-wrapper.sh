#!/bin/bash
set -e

envsubst '$TABLE_ORDERS $TABLE_CUSTOMERS $TABLE_ROLES $TABLE_TG_USERS $TABLE_EMPLOYEES $TABLE_CATEGORIES $TABLE_ITEMS $TABLE_FLAT_ORDERS $DEFAULT_ADMIN_TOKEN $DEFAULT_ADMIN_TG_ID' \
    < "/docker-entrypoint-initdb.d/init.template" \
    > "/tmp/processed-init.sql"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    -f "/tmp/processed-init.sql"
