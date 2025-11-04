#!/usr/bin/env bash

set -e

docker run \
       --rm \
       --env-file free-trial-license-docker.env \
       --net=host \
       -v "$(pwd)/root.json:/home/root.json" \
       -v "$(pwd)/generators:/home/generators" \
       -v "$(pwd)/connections:/home/connections" \
       -v "$(pwd)/functions:/home/functions" \
       -v "$(pwd)/zones:/home/zones" \
       -v "$(pwd)/functions:/home/functions" \
       shadowtraffic/shadowtraffic:latest \
       --config /home/root.json
