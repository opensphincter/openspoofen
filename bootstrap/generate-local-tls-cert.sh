#!/usr/bin/env bash

set -euo pipefail

CERT_DIR="${1:-/etc/openspoofen/tls}"
HOSTNAME_VALUE="${2:-openspoofen.local}"
CERT_PATH="${3:-$CERT_DIR/openspoofen.crt}"
KEY_PATH="${4:-$CERT_DIR/openspoofen.key}"
HOSTNAME_SHORT="${HOSTNAME_VALUE%.local}"
OPENSSL_CONFIG="$(mktemp)"

cleanup() {
    rm -f "$OPENSSL_CONFIG"
}

trap cleanup EXIT

install -d "$(dirname "$CERT_PATH")"
install -d "$(dirname "$KEY_PATH")"

cat >"$OPENSSL_CONFIG" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
CN = $HOSTNAME_VALUE

[v3_req]
subjectAltName = @alt_names
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = $HOSTNAME_VALUE
DNS.2 = $HOSTNAME_SHORT
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF

openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout "$KEY_PATH" \
    -out "$CERT_PATH" \
    -config "$OPENSSL_CONFIG" \
    -extensions v3_req

chmod 600 "$KEY_PATH"
chmod 644 "$CERT_PATH"

echo "Created $CERT_PATH and $KEY_PATH"