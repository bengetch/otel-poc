import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor,
    SpanExporter, SpanExportResult
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    MetricExporter, MetricExportResult, ConsoleMetricExporter, PeriodicExportingMetricReader
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor, LogExporter, LogExportResult, ConsoleLogExporter
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
OTEL_COLLECTOR_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", None)


class NoOpSpanExporter(SpanExporter):
    def export(self, spans):
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


class NoOpMetricExporter(MetricExporter):
    def export(self, metrics_data, timeout_millis: float = 10_000, **kwargs):
        return MetricExportResult.SUCCESS

    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        pass

    def shutdown(self, timeout_millis: float = 30_000, **kwargs):
        pass


class NoOpLogExporter(LogExporter):
    def export(self, batch):
        return LogExportResult.SUCCESS

    def shutdown(self):
        pass


def resolve_span_exporter():

    trace.set_tracer_provider(TracerProvider())
    span_exporter_type = os.getenv("SPAN_EXPORTER")
    if span_exporter_type == "OTLP":
        # collector endpoint used by the OTLPSpanExporter is set by the
        # `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable. if this
        # variable is not set, we default to the NoOpSpanExporter
        if OTEL_COLLECTOR_ENDPOINT is None:
            logger.warning(
                "SPAN_EXPORTER set to OTLP, but OTEL_EXPORTER_OTLP_ENDPOINT is not set. "
                "Defaulting to NoOp span export."
            )
            exporter = SimpleSpanProcessor(NoOpSpanExporter())
        else:
            exporter = BatchSpanProcessor(OTLPSpanExporter())
    elif span_exporter_type == "CONSOLE":
        exporter = SimpleSpanProcessor(ConsoleSpanExporter())
    else:
        exporter = SimpleSpanProcessor(NoOpSpanExporter())

    trace.get_tracer_provider().add_span_processor(exporter)
    return trace.get_tracer_provider().get_tracer(os.getenv("TRACER_NAME", "UNNAMED_TRACER"))


def resolve_metrics_exporter():

    metrics_exporter_type = os.getenv("METRICS_EXPORTER")
    if metrics_exporter_type == "OTLP":
        # collector endpoint used by the OTLPMetricExporter is set by the
        # `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable. if this
        # variable is not set, we default to the NoOpMetricExporter
        if OTEL_COLLECTOR_ENDPOINT is None:
            logger.warning(
                "METRICS_EXPORTER set to OTLP, but OTEL_EXPORTER_OTLP_ENDPOINT is not set. "
                "Defaulting to NoOp metrics export."
            )
            metrics_exporter = NoOpMetricExporter()
        else:
            metrics_exporter = OTLPMetricExporter(insecure=True)
    elif metrics_exporter_type == "CONSOLE":
        metrics_exporter = ConsoleMetricExporter()
    else:
        metrics_exporter = NoOpMetricExporter()

    metrics.set_meter_provider(
        MeterProvider(
            metric_readers=[PeriodicExportingMetricReader(metrics_exporter)]
        )
    )

    return metrics.get_meter_provider().get_meter(os.getenv("METER_NAME", "UNNAMED_METER"))


def resolve_logs_exporter():

    logs_exporter_type = os.getenv("LOGS_EXPORTER")
    if logs_exporter_type == "OTLP":
        # collector endpoint used by the OTLPLogExporter is set by the
        # `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable. if this
        # variable is not set, we default to the NoOpLogExporter
        if OTEL_COLLECTOR_ENDPOINT is None:
            logger.warning(
                "LOGS_EXPORTER set to OTLP, but OTEL_EXPORTER_OTLP_ENDPOINT is not set. "
                "Defaulting to NoOp logs export."
            )
            exporter = NoOpLogExporter()
        else:
            exporter = OTLPLogExporter(insecure=True)
    elif logs_exporter_type == "CONSOLE":
        exporter = ConsoleLogExporter()
    else:
        exporter = NoOpLogExporter()

    logger_provider = LoggerProvider()
    set_logger_provider(logger_provider)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    return LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
