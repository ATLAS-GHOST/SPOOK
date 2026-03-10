#!/bin/sh

/opt/otelcol --config /etc/otel/config.yaml &

/opt/prometheus/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/opt/prometheus/data \
    --web.listen-address=:9090 \
    --web.enable-admin-api &


exec "$@"