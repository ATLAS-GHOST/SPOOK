#!/bin/bash

CONTAINER_NAME="monitoring"
SNAPSHOT_DIR="$1" 

if [ -z "$SNAPSHOT_DIR" ]; then
    echo "Usage: $0 <snapshot-folder>"
    exit 1
fi

echo "Stopping Prometheus container..."
docker stop "$CONTAINER_NAME"

echo "Clearing old data..."
docker exec "$CONTAINER_NAME" rm -rf /opt/prometheus/data/*

echo "Copying snapshot into container..."
docker cp "$SNAPSHOT_DIR"/. "$CONTAINER_NAME":/opt/prometheus/data/

echo "Starting Prometheus container..."
docker start "$CONTAINER_NAME"

echo "Snapshot restored and Prometheus is running."