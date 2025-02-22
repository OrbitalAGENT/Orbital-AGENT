#!/bin/bash
set -eo pipefail

install_system_deps() {
    if command -v apt &>/dev/null; then
        sudo apt update
        sudo apt install -y build-essential libssl-dev zlib1g-dev
    elif command -v yum &>/dev/null; then
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y openssl-devel zlib-devel
    fi
}

install_python_deps() {
    pip install -r requirements.txt
}

main() {
    install_system_deps
    install_python_deps
}

main "$@"
