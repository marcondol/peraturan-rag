# Runbook: Insiden LLM (draf Minggu 3 — lengkapi dengan angka nyata
# setelah Minggu 1–2 berjalan)

## 1. Halusinasi massal / jawaban ngawur naik

- **Deteksi:** skor eval faithfulness turun di Langfuse dataset runs;
  alert Grafana: eval regression.
- **Mitigasi cepat:** rollback prompt ke versi sebelumnya di Langfuse
  (prompt versioning v1, v2…) — tanpa redeploy app.
- **Investigasi:** buka trace yang skornya rendah, cek dokumen yang
  ter-retrieve (salah top_k? dokumen usang?) dan model yang dipakai.
- **Tindak lanjut:** tambah pertanyaan gagal ke `evals/dataset.jsonl`,
  perbaiki dokumen KB atau retrieval, re-run eval.

## 2. Cost spike (token/biaya per request melonjak)

- **Deteksi:** alert Grafana: cost/request di atas ambang; Langfuse
  usage per trace.
- **Mitigasi cepat:** batasi `top_k` / panjang konteks, turunkan
  `max_tokens`, atau alihkan sementara ke model yang lebih murah.
- **Investigasi:** trace dengan prompt_tokens terbesar — loop
  retrieval? prompt bocor? konteks duplikat?
- **Tindak lanjut:** catat di `docs/capacity-tco.md`, sesuaikan budget.

## 3. Model down (vLLM / Gemini tidak merespons)

- **Deteksi:** alert Grafana: error rate /ask naik; health check
  `/health` gagal; Datadog vLLM metrics (lapisan serving) ikut merah.
- **Mitigasi cepat:** alihkan LLM_BACKEND ke backend cadangan
  (vLLM ↔ Gemini) via env + restart; mode demo menjaga endpoint
  tetap menjawab sambil diperbaiki.
- **Investigasi:** cek log vLLM (GPU util, VRAM, waiting queue —
  metrik yang sudah dimonitor via Datadog) atau status API Gemini.
- **Tindak lanjut:** tulis postmortem singkat + tambah ke dataset eval
  bila ada jawaban yang terdampak.
