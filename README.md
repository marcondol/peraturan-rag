# RAG + LLM Observability (Langfuse, OpenTelemetry, K3s)

Proyek sprint 2–3 minggu dari `rag-langfuse-sprint-plan.md`: RAG chatbot
end-to-end dengan observabilitas LLM lapisan aplikasi — trace per prompt,
token & cost tracking per request, prompt versioning, dan evaluasi
LLM-as-judge — sebagai bukti langsung untuk lowongan SRE Rakuten Analytics
(TEKsystems), yang mensyaratkan salah satu dari Langfuse / LangSmith /
Arize / Phoenix secara self-hosted.

## Arsitektur

```
Pengguna → FastAPI RAG service (app/)
              ├─ retrieval: pgvector (Postgres) atau fallback keyword
              │  atas docs-kb/ bila DB belum ada
              ├─ LLM: vLLM ATAU OpenRouter (OpenAI-compatible, dipakai
              │  malam 25 Nov 2026 — satu key, termasuk Gemini) ATAU
              │  Gemini API (pilih satu via LLM_BACKEND)
              └─ instrumentasi: OpenTelemetry SDK → OTel Collector
                                   ├─ Langfuse self-hosted (K3s/Compose)
                                   ├─ Prometheus/Grafana (spanmetrics, SLO)
                                   └─ export idempotent → Postgres
```

Langfuse v3 = 6 container: web, worker, Postgres, ClickHouse, Redis,
MinIO. Butuh ±4 GB RAM / 2–4 vCPU untuk beban homelab — jangan jalankan
di K3s yang tipis; opsi: Langfuse di VPS/GCP dulu, app di K3s.
Versi di-pin ke **Langfuse 3.x** (3.224.x per Okt 2026); v4 mengubah
model data ClickHouse, jadi jangan upgrade tanpa verifikasi.

## Runbook malam 25 Nov 2026 (mini PC, skenario audit keuangan)

Keputusan Arif: mini PC + Cloudflare Zero Trust + domain sendiri,
GitHub + GitHub Actions (self-hosted runner — runner GitHub biasa
tidak bisa menjangkau jaringan rumah), Postgres via Docker (yang
lama mati, compose sudah mendefinisikan `pgvector/pgvector:pg16`).

```bash
cp .env.example .env        # isi: LLM_BACKEND=openrouter,
                            # OPENROUTER_API_KEY, LLM_MODEL=google/gemini-2.5-flash
# 1. DB + service:
docker compose up --build -d
# 2. Korpus: unduh PDF UU 17/2003, UU 1/2004, UU 15/2004,
#    Perpres 16/2018, PMK SBM 32/2025 dari peraturan.go.id / jdih,
#    konversi ke .txt, taruh di docs-kb/keuangan/
#    (petunjuk lengkap di docs-kb/keuangan/README.md)
# 3. Ingest:
cd app && python ingest.py && cd ..
# 4. Tes pertama (dengan sitasi pasal):
curl -X POST localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question": "Berapa uang harian perjalanan dinas ke Padang?"}'
# 5. Push repo publik -> CI hijau -> pasang self-hosted runner di
#    mini PC -> tambah job deploy di .github/workflows/ -> Langfuse
#    naik (compose resmi) -> rute via Cloudflare tunnel.
```

Catatan: `ingest.py` + retrieval pgvector sudah ditulis (25 Nov,
siang) — malam ini tidak ada lagi TODO kode. Yang belum teruji di
mesin Arif: koneksi OpenRouter dari mini PC, embedding model
`openai/text-embedding-3-small` di akunnya, dan `docker compose up`.
Bila `/ask` mengembalikan jawaban tanpa sitasi pgvector, cek
`RAG_DATABASE_URL` dan isi tabel `rag_documents` dulu — service
sengaja fallback ke keyword bila DB belum siap, bukan error.

## Quickstart (Minggu 1, hari 1)

```bash
cp .env.example .env        # isi LLM_BACKEND + kredensial
# 1. Langfuse (pakai compose resmi upstream, jangan salin manual):
bash infra/langfuse/fetch-official-compose.sh
cd infra/langfuse && docker compose up -d && cd ../..
# 2. RAG service + pgvector:
docker compose up --build -d
# 3. Coba satu query:
curl -X POST localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question": "Apa beda Sidekiq dan Kafka?"}'
# 4. Buka Langfuse di localhost:3000 → cari trace-nya.
```

Tanpa Langfuse / LLM yang terkonfigurasi, service tetap jalan dalam
mode demo: retrieval fallback keyword atas `docs-kb/`, jawaban dari
model yang tersedia, dan trace hanya dicatat bila Langfuse aktif.
Ini sengaja — demo pertama tidak boleh terblokir setup infra.

## Struktur

| Path | Isi |
|---|---|
| `app/` | FastAPI service: `main.py`, `rag.py`, `llm.py`, `tracing.py` |
| `docs-kb/` | Dokumen contoh untuk retrieval pertama |
| `evals/` | Dataset eval (target 30–50 Q&A) + `judge.py` (LLM-as-judge) |
| `infra/langfuse/` | Script ambil compose resmi + `.env` Langfuse |
| `infra/helm/langfuse/` | Values awal untuk Helm chart Langfuse di K3s |
| `docs/` | ADR, runbook insiden LLM, model capacity & TCO |
| `dashboards/` | (Minggu 2) Grafana SLO + alert |

## Keputusan yang masih terbuka (tidak memblokir)

- **LLM_BACKEND**: `openrouter` — DIPUTUSKAN 25 Nov 2026 (Gemini via
  OpenRouter, beberapa akun). vLLM di GPU cluster tetap jadi opsi
  nanti; `gemini` langsung tetap didukung.
- **Lokasi Langfuse**: K3s (Helm) atau VPS/GCP (Compose) — tergantung
  sisa RAM/disk K3s.
- Tiga pertanyaan CV soal Datadog + vLLM (metrik, skala, token/cost
  tracking) tetap menunggu jawabanmu — tidak menghalangi sprint.

## Bukti yang dihasilkan sprint ini

- Minggu 1: screenshot trace Langfuse + satu query yang bisa didemo.
- Minggu 2: dashboard SLO + laporan eval pertama.
- Minggu 3: repo publik + studi kasus 1 halaman + demo 5 menit (EN).
