import random
import time
import argparse
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter


def main(collector_ip):
    user_endpoint = f"http://{collector_ip}:4318/v1/metrics"

    exporter = OTLPMetricExporter(endpoint=user_endpoint)

    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=1000
    )

    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)

    meter = metrics.get_meter("fake_docker")


    container_cpu = meter.create_gauge("container_cpu_usage")

    container_mem = meter.create_gauge("container_memory_usage_bytes")

    while True:

        container_cpu.set(random.uniform(5, 80), {"container": "monitoring"})
        container_mem.set(random.uniform(200_000_000, 900_000_000), {"container": "monitoring"})

        time.sleep(0.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fake Docker Metrics Sender")
    parser.add_argument("--collector_ip", default="localhost", help="IP address of OTLP collector (default: localhost)")

    args = parser.parse_args()

    main(args.collector_ip)
