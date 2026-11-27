# Capacity & TCO model — trace volume 1x / 10x / 100x (draf Minggu 3)

Angka dasar (cek ulang sebelum dikirim ke recruiter):
- ClickHouse tumbuh **1–2 GB per 1 juta trace** (tutorial Langfuse v3,
  2026; tergantung ukuran prompt/completion).
- Langfuse v3 homelab: **±4 GB RAM / 2–4 vCPU**, disk awal 100 GB.
- Harga LLM per 1M token: isi dari provider-mu di `.env`
  (`LLM_PRICE_*`) — JANGAN pakai angka fiktif di sini.

## Skenario (asumsi: 1 trace = 1 request /ask)

| Skenario | Trace/bulan | Storage ClickHouse/bulan | Storage 12 bulan* |
|---|---|---|---|
| 1x (demo/pribadi) | 10.000 | ~0,02 GB | ~0,2 GB |
| 10x (tim kecil) | 100.000 | ~0,2 GB | ~2 GB |
| 100x (produksi kecil) | 1.000.000 | ~1–2 GB | ~12–24 GB |

\* Tanpa retention/compaction; dengan retention 90 hari, angka 12 bulan
jauh lebih kecil — atur retention di Langfuse sejak awal (sesuai JD:
retention enforcement).

## Biaya LLM (isi setelah Minggu 1 — dari cost/request nyata)

| Skenario | Token/request (rata-rata nyata) | Biaya/bulan |
|---|---|---|
| 1x | … (ukur dari trace) | … |
| 10x | … | … |
| 100x | … | … |

## Keputusan yang dicatat

- Retention trace: 90 hari (default awal; sesuaikan dengan kebijakan).
- Export idempotent Langfuse → Postgres (Minggu 2) supaya analitik
  tidak bergantung pada retensi ClickHouse.
- Bila volume melewati 1 jt trace/bulan: evaluasi ClickHouse
  terpisah / managed, bukan menaikkan RAM node K3s tanpa batas.
