#!/bin/bash

CONTAINER_NAME="dnsmasq"
CONTAINER_EXIST=`docker ps --all --quiet --filter name="${CONTAINER_NAME}"`


if [ "${CONTAINER_EXIST}" ]; then
  echo "Container '${CONTAINER_NAME}' Exist"

  # if [ "$(docker ps -aq -f status=exited -f name=${CONTAINER_NAME})" ]; then
  #   # Cleanup
  #   docker rm "${CONTAINER_NAME}"
  # fi

  docker start "${CONTAINER_NAME}"

else
  docker run \
    -d \
    --privileged \
    --net host \
    --name dnsmasq \
    -v /srv/containers/dnsmasq/config:/config \
    dnsmasq-arm64:latest
fi

