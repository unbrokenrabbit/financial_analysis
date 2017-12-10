#!/bin/bash

docker run \
    --name financial-analysis \
    --network=financial-analysis-network \
    --rm \
    -ti \
    -v $PWD/../../project:/src \
    financial_analysis_dev \
    bash

