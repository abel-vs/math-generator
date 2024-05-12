#!/bin/bash

# Define variables
IMAGE_NAME="math-generator:latest"
CONTAINER_NAME="math"

# Build the new Docker image
docker build -t $IMAGE_NAME .

# Stop the running container, ignore error if container does not exist
docker stop $CONTAINER_NAME || true

# Remove the stopped container, ignore error if container does not exist
docker rm $CONTAINER_NAME || true

# Run a new container with the newly built image
docker run -d -p 8501:8501 --name $CONTAINER_NAME --env-file .env $IMAGE_NAME

