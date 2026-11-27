"""Observability wiring: OpenTelemetry + Langfuse.

- OTel: aktif hanya bila OTEL_EXPORTER_OTLP_ENDPOINT diisi; kalau
  tidak, tracer no-op (service tetap jalan).
- Langfuse: aktif hanya bila LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY
  + LANGFUSE_HOST diisi; kalau tidak, fungsi mengembalikan None.
- PII redaction: JANGAN kirim payload mentah yang berisi data pribadi
  ke Langfuse/OTel tanpa masking — masking diterapkan di Collector
  (lihat infra) dan di sini input trace hanya question, bukan
  dokumen internal. Untuk data sensitif, aktifkan masking Langfuse
  (Project Settings > Masking) sebelum demo ke pihak luar.
"""

import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


def init_tracing(service_name: str):
    trace.set_tracer_provider(TracerProvider())
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if endpoint:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
        )
    return trace.get_tracer(service_name)


def init_langfuse():
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")
    host = os.environ.get("LANGFUSE_HOST", "")
    if not (public_key and secret_key and host):
        return None
    from langfuse import Langfuse

    return Langfuse(public_key=public_key, secret_key=secret_key, host=host)


def estimate_cost_usd(backend: str, model: str, usage: dict) -> float:
    """USD per request. Harga per 1M token dari env (isi harga sebenarnya
    dari provider-mu); default 0 = biaya tidak diketahui, bukan nol."""
    prompt_price = float(os.environ.get("LLM_PRICE_PROMPT_PER_1M", "0"))
    completion_price = float(os.environ.get("LLM_PRICE_COMPLETION_PER_1M", "0"))
    return round(
        usage["prompt_tokens"] * prompt_price / 1_000_000
        + usage["completion_tokens"] * completion_price / 1_000_000,
        6,
    )
