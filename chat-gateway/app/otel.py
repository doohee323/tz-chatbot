"""OpenTelemetry tracing. Enabled when OTEL_EXPORTER_OTLP_ENDPOINT is set."""
import logging
import os

logger = logging.getLogger("chat_gateway")

_TRACER_PROVIDER_SET = False


def setup_otel(app, *, service_name: str = "chat-gateway") -> None:
    """Configure OpenTelemetry and instrument the FastAPI app. No-op if OTEL_EXPORTER_OTLP_ENDPOINT unset."""
    endpoint = (os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or "").strip()
    if not endpoint:
        logger.debug("OpenTelemetry disabled (OTEL_EXPORTER_OTLP_ENDPOINT not set)")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as e:
        logger.warning("OpenTelemetry packages not installed: %s", e)
        return

    global _TRACER_PROVIDER_SET
    if _TRACER_PROVIDER_SET:
        FastAPIInstrumentor.instrument_app(app)
        return

    name = os.environ.get("OTEL_SERVICE_NAME", service_name).strip() or service_name
    resource = Resource.create({"service.name": name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    _TRACER_PROVIDER_SET = True
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry enabled (service=%s, endpoint=%s)", name, endpoint)
