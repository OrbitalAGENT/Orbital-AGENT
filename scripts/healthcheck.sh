#!/bin/bash
set -eo pipefail

PORT=${PORT:-8080}
TIMEOUT=${TIMEOUT:-5}

check_port() {
    nc -z -w "$TIMEOUT" localhost "$PORT"
}

check_api() {
    curl -sSf -m "$TIMEOUT" "http://localhost:$PORT/health"
}

check_dependencies() {
    pgrep -f "redis-server" >/dev/null
    pgrep -f "kafka" >/dev/null
}

main() {
    check_port
    check_api
    check_dependencies
}

main "$@"
