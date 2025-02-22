#!/bin/bash
set -eo pipefail

LOG_FILE="/var/log/orbital/monitor.log"

check_resources() {
    echo "[$(date)] CPU Usage: $(top -bn1 | grep load | awk '{printf "%.2f", $(NF-2)}')"
    echo "[$(date)] Memory Usage: $(free -m | awk '/Mem/{printf "%.2f%%", \$3/\$2*100}')"
}

check_services() {
    pgrep -x "orbital-agent" >/dev/null || echo "Agent process not running!"
    systemctl is-active --quiet docker || echo "Docker not running!"
}

main() {
    {
        check_resources
        check_services
    } >> "$LOG_FILE"
}

main "$@"
