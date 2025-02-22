#!/bin/bash
set -eo pipefail

clean_build() {
    rm -rf dist/ build/ *.egg-info
}

clean_docker() {
    docker system prune -af
}

clean_logs() {
    find /var/log/orbital -type f -name "*.log*" -mtime +30 -delete
}

main() {
    clean_build
    clean_docker
    clean_logs
}

main "$@"
