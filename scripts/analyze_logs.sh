#!/bin/bash
set -eo pipefail

LOG_FILE=${1:-"/var/log/orbital/app.log"}

analyze_errors() {
    awk '/ERROR/ {count++} END {print "Total Errors:", count}' "$LOG_FILE"
}

analyze_warnings() {
    awk '/WARN/ {count++} END {print "Total Warnings:", count}' "$LOG_FILE"
}

analyze_requests() {
    awk '/GET|POST/ {count++} END {print "Total Requests:", count}' "$LOG_FILE"
}

main() {
    echo "=== Log Analysis Report ==="
    analyze_errors
    analyze_warnings 
    analyze_requests
}

main "$@"
