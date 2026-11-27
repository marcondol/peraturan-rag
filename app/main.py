"""RAG service: FastAPI + retrieval + LLM + observability.

Satu endpoint utama: POST /ask -> jawaban + sitasi + token/cost.
Setiap request menghasilkan satu trace Langfuse (bila dikonfigurasi)
dan satu span OpenTelemetry. Tanpa Langfuse/LLM, service tetap jalan
(mode demo) supaya demo pertama tidak terblokir setup infra.
"""

import os
import time

from fastapi import FastAPI
from pydantic import BaseModel, Field

from llm import LLMClient, LLMUnavailable
from rag import retrieve
from tracing import estimate_cost_usd, init_langfuse, init_tracing

PROMPT_VERSION = os.environ.get("PROMPT_VERSION", "v1")

app = FastAPI(title="rag-llm-observability", version="0.1.0")
tracer = init_tracing("rag-service")
langfuse = init_langfuse()
llm = LLMClient.from_env()

SYSTEM_PROMPT = (
    "Jawab hanya berdasarkan konteks yang diberikan. "
    "Bila konteks tidak cukup, katakan tidak tahu. "
    "Sertakan nomor dokumen sumber di akhir jawaban."
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    top_k: int = Field(5, ge=1, le=10)


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_ms: int
    prompt_version: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_backend": llm.backend,
        "langfuse": bool(langfuse),
        "prompt_version": PROMPT_VERSION,
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    started = time.monotonic()
    trace = langfuse.trace(name="rag-ask", input=req.question) if langfuse else None
    with tracer.start_as_current_span("rag.ask") as span:
        span.set_attribute("prompt.version", PROMPT_VERSION)
        span.set_attribute("rag.top_k", req.top_k)

        docs = retrieve(req.question, top_k=req.top_k)
        context = "\n\n".join(f"[{d['id']}] {d['text']}" for d in docs)
        prompt = f"{SYSTEM_PROMPT}\n\nKonteks:\n{context}\n\nPertanyaan: {req.question}"

        try:
            result = llm.generate(prompt)
        except LLMUnavailable as exc:
            if trace:
                trace.update(output=f"LLM unavailable: {exc}")
            raise

        usage = result.usage
        cost = estimate_cost_usd(llm.backend, llm.model, usage)
        latency_ms = int((time.monotonic() - started) * 1000)

        span.set_attribute("llm.prompt_tokens", usage["prompt_tokens"])
        span.set_attribute("llm.completion_tokens", usage["completion_tokens"])
        span.set_attribute("llm.cost_usd", cost)
        span.set_attribute("llm.latency_ms", latency_ms)

        if trace:
            trace.update(
                output=result.text,
                metadata={
                    "prompt_version": PROMPT_VERSION,
                    "model": llm.model,
                    "sources": [d["id"] for d in docs],
                    "usage": usage,
                    "cost_usd": cost,
                    "latency_ms": latency_ms,
                },
            )

        return AskResponse(
            answer=result.text,
            sources=[d["id"] for d in docs],
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            cost_usd=cost,
            latency_ms=latency_ms,
            prompt_version=PROMPT_VERSION,
        )
