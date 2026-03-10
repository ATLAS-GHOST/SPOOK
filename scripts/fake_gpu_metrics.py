import random
import time

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

# OTLP exporter
exporter = OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")

reader = PeriodicExportingMetricReader(
    exporter,
    export_interval_millis=1000  # flush every 1 second
)

# Meter provider
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter("fake_gpu")

# GPU metrics
gpu_util = meter.create_gauge("gpu_utilization")          # %
gpu_mem_used = meter.create_gauge("gpu_memory_used")      # MB
gpu_mem_total = meter.create_gauge("gpu_memory_total")    # MB
gpu_temp = meter.create_gauge("gpu_temperature")          # Celsius
gpu_power = meter.create_gauge("gpu_power_usage")         # Watts
gpu_bandwidth = meter.create_gauge("gpu_bandwidth")       # GB/s
gpu_pcie_tx = meter.create_gauge("gpu_pcie_tx")           # GB/s
gpu_pcie_rx = meter.create_gauge("gpu_pcie_rx")           # GB/s
gpu_nvlink_tx = meter.create_gauge("gpu_nvlink_tx")       # GB/s
gpu_nvlink_rx = meter.create_gauge("gpu_nvlink_rx")       # GB/s


while True:


    gpu_util.set(random.uniform(20, 90), {"gpu": "0"})
    gpu_mem_total.set(16384, {"gpu": "0"})  # fake 16GB GPU
    gpu_mem_used.set(random.uniform(1000, 12000), {"gpu": "0"})
    gpu_temp.set(random.uniform(40, 85), {"gpu": "0"})
    gpu_bandwidth.set(random.uniform(250, 950), {"gpu": "0"})
    gpu_power.set(random.uniform(50, 250), {"gpu": "0"})
    gpu_pcie_tx.set(random.uniform(100, 950), {"gpu": "0"})
    gpu_pcie_rx.set(random.uniform(100, 950), {"gpu": "0"})
    gpu_nvlink_tx.set(random.uniform(100, 950), {"gpu": "0"})
    gpu_nvlink_rx.set(random.uniform(100, 950), {"gpu": "0"})
