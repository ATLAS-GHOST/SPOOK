#!/bin/bash

# Start Node Exporter
/opt/node_exporter/node_exporter &

# Start Prometheus in background
/opt/prometheus/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/opt/prometheus/data \
    --web.listen-address=:9090 &

# Start Grafana in background
/opt/grafana/bin/grafana-server \
    --homepath=/opt/grafana \
    --config=/opt/grafana/conf/defaults.ini \
    web &

# Execute whatever command was passed (or default CMD)
exec "$@"