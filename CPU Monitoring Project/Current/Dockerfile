FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y wget tar && rm -rf /var/lib/apt/lists/*

# Install Prometheus
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz && \
    tar xvfz prometheus-2.48.0.linux-amd64.tar.gz && \
    mv prometheus-2.48.0.linux-amd64 /opt/prometheus && \
    rm prometheus-2.48.0.linux-amd64.tar.gz

# Install Grafana
RUN wget https://dl.grafana.com/oss/release/grafana-10.2.2.linux-amd64.tar.gz && \
    tar -zxvf grafana-10.2.2.linux-amd64.tar.gz && \
    mv grafana-v10.2.2 /opt/grafana && \
    rm grafana-10.2.2.linux-amd64.tar.gz

# Install Node Exporter for network metrics
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz && \
    tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz && \
    mv node_exporter-1.7.0.linux-amd64 /opt/node_exporter && \
    rm node_exporter-1.7.0.linux-amd64.tar.gz

# Create prometheus config directory
RUN mkdir -p /etc/prometheus

# Copy prometheus config (you need to have this file next to Dockerfile)
COPY prometheus.yml /etc/prometheus/prometheus.yml

# Create Grafana datasource config
RUN mkdir -p /opt/grafana/conf/provisioning/datasources
COPY <<EOF /opt/grafana/conf/provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
EOF

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh



EXPOSE 9090 3000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["sleep", "infinity"]