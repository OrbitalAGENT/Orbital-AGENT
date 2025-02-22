#!/bin/bash
set -eo pipefail

CONFIG_PATH=${CONFIG_PATH:-"/etc/orbital"}
LOG_LEVEL=${LOG_LEVEL:-"info"}

validate_config() {
    if [ ! -f "$CONFIG_PATH/config.yaml" ]; then
        echo "Configuration file not found at $CONFIG_PATH/config.yaml"
        exit 1
    fi
}

start_service() {
    exec /usr/bin/orbital-agent \
        --config "$CONFIG_PATH/config.yaml" \
        --log-level "$LOG_LEVEL"
}

main() {
    validate_config
    start_service
}

main "$@"
