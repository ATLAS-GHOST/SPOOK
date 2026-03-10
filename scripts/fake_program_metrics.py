import random
import time

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter


exporter = OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")

reader = PeriodicExportingMetricReader(
    exporter,
    export_interval_millis=1000
)

provider = MeterProvider(
    metric_readers=[reader],
    views=[
        View(
            instrument_name="program_packet_latency_ms",
            aggregation=ExplicitBucketHistogramAggregation(
                boundaries=[1,2,3,4,5,6,7,8,9,10]
            )
        )
    ],
)

metrics.set_meter_provider(provider)

meter = metrics.get_meter("program_metrics")


# Program metrics
packets_dropped = meter.create_counter("program_packets_dropped")

processing_latency = meter.create_histogram("program_packet_latency_ms")

packets_per_second = meter.create_gauge("program_packets_per_second")

cpu_util = meter.create_gauge("program_cpu_utilization")


while True:

    packets_per_second.set(random.randint(10000,80000))

    if random.random() < 0.02:
        packets_dropped.add(1)

    processing_latency.record(max(0, random.gauss(5,1)))

    cpu_util.set(random.uniform(10,70))

    time.sleep(1)
