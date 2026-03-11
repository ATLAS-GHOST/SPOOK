FROM alpine:3.23.3

RUN wget https://github.com/prometheus/prometheus/releases/download/v3.5.1/prometheus-3.5.1.linux-amd64.tar.gz && \
    tar xvfz prometheus-3.5.1.linux-amd64.tar.gz && \
    mv prometheus-3.5.1.linux-amd64 /opt/prometheus && \
    rm prometheus-3.5.1.linux-amd64.tar.gz

RUN wget https://dl.grafana.com/grafana/release/12.3.3/grafana_12.3.3_21957728731_linux_amd64.tar.gz && \
    tar -zxvf grafana_12.3.3_21957728731_linux_amd64.tar.gz && \
    mv grafana-12.3.3 /opt/grafana && \
    rm grafana_12.3.3_21957728731_linux_amd64.tar.gz

RUN wget https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.147.0/otelcol_0.147.0_linux_amd64.tar.gz && \
    tar -xvf otelcol_0.147.0_linux_amd64.tar.gz && \
    mv otelcol /opt/otelcol && \
    rm otelcol_0.147.0_linux_amd64.tar.gz

RUN mkdir -p /etc/prometheus

COPY prometheus.yml /etc/prometheus/prometheus.yml

RUN mkdir -p /opt/grafana/conf/provisioning/datasources
COPY datasources.yml /opt/grafana/conf/provisioning/datasources/prometheus.yml

RUN mkdir -p /opt/grafana/conf/provisioning/dashboards
COPY dashboards.yml /opt/grafana/conf/provisioning/dashboards/dashboards.yml
COPY dashboard.json /opt/grafana/conf/provisioning/dashboards/dashboard.json    

COPY otel-collector-config.yaml /etc/otel/config.yaml


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/opt/grafana/bin/grafana-server", "--homepath=/opt/grafana", "--config=/opt/grafana/conf/defaults.ini", "web"]