import random
import time
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter


exporter = OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")

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
