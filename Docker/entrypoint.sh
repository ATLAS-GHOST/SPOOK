#!/bin/sh

# Start Prometheus 
echo "Starting Prometheus..."
/opt/prometheus/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/opt/prometheus/data \
    --web.listen-address=:9090 &

# Start Grafana 
echo "Starting Grafana..."
/opt/grafana/bin/grafana-server \
    --homepath=/opt/grafana \
    --config=/opt/grafana/conf/defaults.ini \
    web &

exec "$@"