#!/usr/bin/env bash
set -eu

docker build \
  --compress \
  --force-rm \
  --platform=linux/arm64 \
  --file Dockerfile.yml \
  --tag "dnsmasq-arm64" \
  .
