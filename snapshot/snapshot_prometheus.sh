#!/bin/bash

CONTAINER_NAME="monitoring"

HOST_SNAPSHOT_DIR="./prometheus_snapshot"

mkdir -p "$HOST_SNAPSHOT_DIR"

# Trigger snapshot via Prometheus admin API
SNAPSHOT_JSON=$(curl -s -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot) 

# Parse snapshot ID from JSON
SNAPSHOT_ID=$(echo "$SNAPSHOT_JSON" | grep -oP '(?<="name":")[^"]+')

if [ -z "$SNAPSHOT_ID" ]; then
    echo "Snapshot creation failed or admin API not enabled."
    exit 1
fi

echo "Snapshot created with ID: $SNAPSHOT_ID"

# Copy snapshot from container to host folder
docker cp "$CONTAINER_NAME":/opt/prometheus/data/snapshots/"$SNAPSHOT_ID" "$HOST_SNAPSHOT_DIR"/"$SNAPSHOT_ID"

echo "Snapshot copied to $HOST_SNAPSHOT_DIR/$SNAPSHOT_ID"

# Optional: compress snapshot
# tar czf "$HOST_SNAPSHOT_DIR/$SNAPSHOT_ID.tar.gz" -C "$HOST_SNAPSHOT_DIR" "$SNAPSHOT_ID"
# echo "Snapshot compressed to $HOST_SNAPSHOT_DIR/$SNAPSHOT_ID.tar.gz"