#!/bin/bash

docker run \
    --name mongodb-client \
    --network=financial-analysis-network \
    --rm \
    -ti \
    mongodb_client \
    bash

