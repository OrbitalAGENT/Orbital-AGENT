#!/bin/bash
set -eo pipefail

BACKUP_DIR="/var/backups/orbital"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
RETENTION_DAYS=7

create_backup() {
    mkdir -p "$BACKUP_DIR"
    tar -czf "$BACKUP_DIR/orbital-backup-$TIMESTAMP.tar.gz" \
        /etc/orbital \
        /var/lib/orbital
}

clean_old_backups() {
    find "$BACKUP_DIR" -name "orbital-backup-*.tar.gz" -mtime +$RETENTION_DAYS -delete
}

main() {
    create_backup
    clean_old_backups
}

main "$@"
