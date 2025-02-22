#!/bin/bash
set -eo pipefail

DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-"orbital"}
MIGRATIONS_DIR="migrations"

execute_migration() {
    local file=\$1
    echo "Applying $file..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$file"
}

main() {
    if [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
        echo "DB_USER and DB_PASSWORD must be set"
        exit 1
    fi

    export PGPASSWORD="$DB_PASSWORD"
    
    for migration in $(ls "$MIGRATIONS_DIR"/*.sql | sort -V); do
        execute_migration "$migration"
    done
}

main "$@"
