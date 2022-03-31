#!/usr/bin/env bash
set -eu

docker build \
  --compress \
  --force-rm \
  --platform=linux/arm64 \
  --file Dockerfile \
  --tag "dnsmasq-arm64" \
  .