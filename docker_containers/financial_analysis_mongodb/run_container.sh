docker run \
    --name financial-analysis-mongodb \
    --network=financial-analysis-network \
    -v financial-analysis-mongodb-data:/data/db \
    -d \
    mongo:3.6.0

