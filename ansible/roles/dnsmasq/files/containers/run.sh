#!/bin/bash

docker run \
  -d \
  --rm \
  --privileged \
  --name dnsmasq \
  --net=host \
  -v /srv/containers/dnsmasq/config:/config \
  dnsmasq-arm64:latest

#  --cap-add=NET_ADMIN \