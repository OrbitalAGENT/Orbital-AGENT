#!/bin/bash
set -eo pipefail

# Build parameters
BUILD_DIR="dist"
VERSION=$(git describe --tags)
PLATFORM=$(uname -sm | tr ' ' '-')

clean() {
    rm -rf "$BUILD_DIR" || true
}

compile() {
    echo "Compiling for $PLATFORM..."
    mkdir -p "$BUILD_DIR"
    go build -o "$BUILD_DIR/orbital-agent-$VERSION-$PLATFORM" ./cmd/main.go
}

test() {
    echo "Running tests..."
    go test -v ./...
}

package() {
    echo "Creating package..."
    tar -czf "$BUILD_DIR/orbital-agent-$VERSION-$PLATFORM.tar.gz" -C "$BUILD_DIR" .
}

main() {
    clean
    test
    compile
    package
}

main "$@"
