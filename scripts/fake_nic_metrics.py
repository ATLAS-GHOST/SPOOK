import random
import time
import argparse
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

def main(collector_ip):
    exporter = OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")

    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=1000
    )

    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)

    meter = metrics.get_meter("fake_nic")


    packets_rx = meter.create_gauge("nic_rx")
    packets_tx = meter.create_gauge("nic_tx")

    bytes_rx = meter.create_gauge("nic_bytes_rx")
    bytes_tx = meter.create_gauge("nic_bytes_tx")

    errors = meter.create_counter("nic_errors")

    link_util = meter.create_gauge("nic_link_utilization")


    while True:

        rx_pkts = random.randint(10000, 80000)
        tx_pkts = random.randint(5000, 80000)

        packets_rx.set(rx_pkts, {"interface": "eth0"})
        packets_tx.set(tx_pkts, {"interface": "eth0"})

        bytes_rx.set(rx_pkts * random.randint(400,64000), {"interface": "eth0"})
        bytes_tx.set(tx_pkts * random.randint(400,64000), {"interface": "eth0"})

        if random.random() < 0.02:
            errors.add(1, {"interface": "eth0"})

        link_util.set(random.uniform(10, 95), {"interface": "eth0"})

        time.sleep(0.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fake GPU Metrics Sender")
    parser.add_argument("--collector_ip", default="localhost", help="IP address of OTLP collector (default: localhost)")

    args = parser.parse_args()

    main(args.collector_ip)