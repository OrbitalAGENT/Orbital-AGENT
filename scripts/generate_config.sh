#!/bin/bash
set -eo pipefail

TEMPLATE_DIR="config/templates"
OUTPUT_DIR="config/generated"

render_template() {
    local template=\$1
    envsubst < "$TEMPLATE_DIR/$template" > "$OUTPUT_DIR/${template%.template}"
}

main() {
    mkdir -p "$OUTPUT_DIR"
    for template in $(ls "$TEMPLATE_DIR"/*.template); do
        render_template "$(basename "$template")"
    done
}

main "$@"
