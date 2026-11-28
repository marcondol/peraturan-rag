"""LLM client pluggable: vLLM / 9router / OpenRouter (OpenAI-compatible) / Gemini API.

Pilih satu via LLM_BACKEND sebelum demo pertama; keduanya sekaligus
hanya memperlambat. Harga per 1M token diisi dari env agar cost
tracking per request akurat — default 0 (biaya tidak diketahui)
supaya tidak ada angka fiktif di trace.

9router (DIPUTUSKAN 27 Nov 2026, ganti OpenRouter): router self-hosted
Arif di https://9router.marcondol.site/v1, token dari
NINE_ROUTER_API_KEY. Model diatur via LLM_MODEL, default `for-rag`
(combo router: context 1M token, max output 128k, tools + reasoning).
Koneksi + model terverifikasi 27 Nov 2026 (GET /v1/models: HTTP 200,
94 model, for-rag satu-satunya combo "rag"). Chat completions via
for-rag BELUM teruji end-to-end — itu cek pertama sesi malam ini.
Backend openrouter tetap didukung sebagai cadangan.
"""

import os
from dataclasses import dataclass


class LLMUnavailable(Exception):
    pass


@dataclass
class LLMResult:
    text: str
    usage: dict  # {"prompt_tokens": int, "completion_tokens": int}


class LLMClient:
    def __init__(self, backend: str, model: str):
        self.backend = backend
        self.model = model
        self._client = None
        if backend == "vllm":
            from openai import OpenAI

            base_url = os.environ.get("VLLM_BASE_URL", "")
            if not base_url:
                raise LLMUnavailable("VLLM_BASE_URL belum diisi (.env)")
            self._client = OpenAI(base_url=base_url, api_key="not-needed")
        elif backend == "9router":
            from openai import OpenAI

            api_key = os.environ.get("NINE_ROUTER_API_KEY", "")
            if not api_key:
                raise LLMUnavailable("NINE_ROUTER_API_KEY belum diisi (.env)")
            self._client = OpenAI(
                base_url="https://9router.marcondol.site/v1",
                api_key=api_key,
            )
        elif backend == "openrouter":
            from openai import OpenAI

            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            if not api_key:
                raise LLMUnavailable("OPENROUTER_API_KEY belum diisi (.env)")
            self._client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                default_headers={
                    "HTTP-Referer": os.environ.get(
                        "OPENROUTER_REFERER", "http://localhost:8000"
                    ),
                    "X-Title": "rag-llm-observability",
                },
            )
        elif backend == "gemini":
            import google.generativeai as genai

            api_key = os.environ.get("GEMINI_API_KEY", "")
            if not api_key:
                raise LLMUnavailable("GEMINI_API_KEY belum diisi (.env)")
            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel(model)
        elif backend == "demo":
            self._client = None  # mode demo: tanpa LLM, jawaban template
        else:
            raise LLMUnavailable(f"LLM_BACKEND tidak dikenal: {backend}")

    @classmethod
    def from_env(cls) -> "LLMClient":
        backend = os.environ.get("LLM_BACKEND", "demo")
        default_model = {
            "vllm": "Qwen3-30B-A3B-Instruct-2507",
            "9router": "for-rag",
            "openrouter": "google/gemini-2.5-flash",
            "gemini": "gemini-2.5-flash",
        }.get(backend, "gemini-2.5-flash")
        model = os.environ.get("LLM_MODEL", default_model)
        try:
            return cls(backend, model)
        except LLMUnavailable:
            # Jangan matikan service karena LLM belum dikonfigurasi;
            # mode demo menjaga endpoint /ask tetap bisa dicoba.
            return cls("demo", "demo")

    def generate(self, prompt: str) -> LLMResult:
        if self.backend == "demo":
            return LLMResult(
                text=(
                    "[DEMO — LLM belum dikonfigurasi] Atur LLM_BACKEND=9router, "
                    "vllm, openrouter, atau gemini di .env, lalu restart. Prompt yang akan "
                    "dikirim:\n\n" + prompt[:800]
                ),
                usage={"prompt_tokens": 0, "completion_tokens": 0},
            )
        if self.backend in ("vllm", "openrouter", "9router"):
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return LLMResult(
                text=resp.choices[0].message.content or "",
                usage={
                    "prompt_tokens": resp.usage.prompt_tokens or 0,
                    "completion_tokens": resp.usage.completion_tokens or 0,
                },
            )
        # gemini
        resp = self._client.generate_content(prompt)
        usage = getattr(resp, "usage_metadata", None)
        return LLMResult(
            text=resp.text,
            usage={
                "prompt_tokens": getattr(usage, "prompt_token_count", 0) or 0,
                "completion_tokens": getattr(usage, "candidates_token_count", 0) or 0,
            },
        )
