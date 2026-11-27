# ADR-001: Langfuse self-hosted untuk observabilitas LLM

Status: Diterima (16 Nov 2026) — keputusan awal sprint, bisa direvisi
bila jawaban recruiter mengubah syarat wajib.

## Konteks

Lowongan SRE Rakuten Analytics mensyaratkan hands-on men-deploy dan
mengoperasikan salah satu dari Langfuse, LangSmith, Arize AX, atau
Phoenix secara self-hosted, plus pemahaman LLM telemetry (traces,
spans, token/cost tracking, prompt versioning, evaluation workflows).

## Pilihan yang dipertimbangkan

| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **Langfuse (dipilih)** | Self-host penuh, prompt management + datasets + evals dalam satu platform, open source, Helm chart resmi, dipakai sebagai bukti langsung JD | v3 butuh 6 container (Postgres + ClickHouse + Redis + MinIO), berat di K3s tipis |
| LangSmith | Evals & tracing matang | Self-host terbatas/berbayar; sebagian fitur cloud-only |
| Arize Phoenix | Ringan, tracing bagus | Prompt management & evals tidak sekaya Langfuse |
| Arize AX | Enterprise, evals kuat | Berbayar, self-host kompleks |

## Keputusan

Langfuse v3 self-hosted, pin 3.x. Alasan: satu-satunya opsi yang
menutup SEMUA kata kunci JD (self-host + traces + prompt versioning
+ datasets + evals + cost tracking) tanpa biaya lisensi, dan ClickHouse
sekaligus menutup "preferred" ClickHouse di JD.

## Konsekuensi

- Butuh ±4 GB RAM / 2–4 vCPU dan 100 GB disk awal — bila K3s tipis,
  Langfuse jalan di VPS/GCP dulu (Compose resmi), app di K3s.
- v4 mengubah model data ClickHouse: jangan upgrade tanpa verifikasi.
- Keamanan sejak hari pertama: PII redaction, masking, retention,
  RBAC/SSO — sesuai JD, bukan tempelan akhir.
