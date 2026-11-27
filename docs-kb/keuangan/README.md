# Korpus: Peraturan Keuangan Indonesia (untuk audit)

RAG ini menjawab pertanyaan audit atas peraturan keuangan — dengan
sitasi pasal/ayat dari teks resmi. **Jangan isi folder ini dengan
teks yang diketik ulang atau diringkas dari ingatan**: jawaban audit
hanya bisa dipercaya kalau chunk-nya berasal dari teks resmi.

## Peraturan awal (disepakati 25 Nov 2026)

| Peraturan | Tentang |
|---|---|
| UU 17/2003 | Keuangan Negara |
| UU 1/2004 | Perbendaharaan Negara |
| UU 15/2004 | Pemeriksaan Pengelolaan dan Tanggung Jawab Keuangan Negara |
| Perpres 16/2018 (+ perubahannya) | Pengadaan Barang/Jasa Pemerintah |
| PMK SBM 32/2025 | Standar Biaya Masukan 2026 (uang harian, honorarium, dsb.) |

Tambahkan peraturan lain yang istri paling sering pakai — tanyakan
ke dia sebelum malam ini, supaya korpus pertama langsung berguna.

## Cara mengisi (5 menit per peraturan)

1. Unduh PDF resminya dari **peraturan.go.id** atau **jdih.kemenkeu.go.id**
   (untuk PMK SBM, dari JDIH Kemenkeu).
2. Konversi ke teks: `pdftotext -layout UU-17-2003.pdf uu-17-2003.txt`
   (paket `poppler-utils`; kalau belum ada: `sudo apt install poppler-utils`).
   Cek hasil .txt-nya sekilas — kalau hasil konversi berantakan
   (kolom tercampur), perbaiki dulu sebelum ingest.
3. Taruh file .txt/.md di folder ini, mis. `uu-17-2003.txt`.
4. Jalankan dari folder `app/`: `python ingest.py` (default folder ini).
   Ingest ulang aman — chunk lama dengan id sama akan ditimpa.

## Contoh pertanyaan untuk tes pertama

- "Berapa uang harian perjalanan dinas ke Padang menurut PMK SBM?"
- "Kapan pengadaan langsung boleh dipakai menurut Perpres 16/2018?"
- "Apa batas honorarium narasumber?"

Jawaban harus menyebut pasal/ayat sumbernya. Selalu verifikasi ke
teks resmi sebelum dipakai untuk kerja audit.

## Korpus sudah terisi (25 Nov 2026, sore — disiapkan Luna)

Enam file `.txt` sudah ada di folder ini, total **787 chunk** (dihitung
dengan `ingest.chunk_file`, tanpa DB — ingest malam ini yang akan
mengirimnya ke pgvector):

| File | Isi | Chunk |
|---|---|---|
| `uu-17-2003.txt` | UU 17/2003 Keuangan Negara (JDIH Kemenkeu, fulltext) | 55 |
| `uu-1-2004.txt` | UU 1/2004 Perbendaharaan Negara (JDIH Kemenkeu, fulltext) | 55 |
| `uu-15-2004.txt` | UU 15/2004 Pemeriksaan Keuangan Negara (JDIH Kemenkeu, fulltext) | 17 |
| `perpres-16-2018.txt` | Perpres 16/2018 Pengadaan Barang/Jasa (JDIH Kemenkeu, PDF scan/OCR) | 152 |
| `perpres-12-2021-perubahan.txt` | Perpres 12/2021, perubahan atas Perpres 16/2018 | 82 |
| `pmk-32-2025-sbm-2026.txt` | PMK 32/2025 SBM TA 2026 (Ditjen Anggaran Kemenkeu, 110 hlm) | 426 |

## Peraturan tambahan (27 Nov 2026 — disiapkan Luna)

Dua belas file `.txt` baru, total **2.414 chunk** tambahan — korpus
sekarang **18 file, 3.201 chunk** (dihitung dengan `ingest.chunk_file`):

| File | Isi | Chunk |
|---|---|---|
| `uu-15-2006-bpk.txt` | UU 15/2006 tentang Badan Pemeriksa Keuangan (JDIH Kemenkeu, fulltext; Pasal 1-40) | 29 |
| `pp-60-2008-spip.txt` | PP 60/2008 tentang Sistem Pengendalian Intern Pemerintah (JDIH Kemenkeu, fulltext; Pasal 1-56) | 32 |
| `pp-71-2010-sap.txt` | PP 71/2010 tentang Standar Akuntansi Pemerintahan, lengkap dengan Lampiran I-III (DJPK Kemenkeu, PDF 413 hlm) | 983 |
| `pp-8-2006-pelaporan.txt` | PP 8/2006 tentang Pelaporan Keuangan dan Kinerja Instansi Pemerintah (JDIH Kemenkeu, fulltext; Pasal 1-38) | 28 |
| `pp-45-2013-apbn.txt` | PP 45/2013 tentang Tata Cara Pelaksanaan APBN, teks asli (JDIH Kemenkeu, fulltext; Pasal 1-182) | 126 |
| `pp-50-2018-perubahan-apbn.txt` | PP 50/2018, perubahan atas PP 45/2013 (Database Peraturan BPK, PDF 31 hlm) | 47 |
| `perbpk-1-2017-spkn.txt` | Peraturan BPK 1/2017 tentang Standar Pemeriksaan Keuangan Negara, lengkap dengan Lampiran I-IV (Database Peraturan BPK, PDF 85 hlm) | 162 |
| `pmk-113-2012-perjadin.txt` | PMK 113/2012 tentang Perjalanan Dinas Dalam Negeri, teks asli (DJPb Kemenkeu, PDF 41 hlm; Pasal 1-43) | 93 |
| `pmk-119-2023-perubahan-perjadin.txt` | PMK 119/2023, perubahan atas PMK 113/2012 (Database Peraturan BPK, PDF 12 hlm) | 29 |
| `pmk-62-2023-perencanaan-pelaksanaan-akuntansi.txt` | PMK 62/2023 tentang Perencanaan Anggaran, Pelaksanaan Anggaran, serta Akuntansi dan Pelaporan Keuangan — hanya badan peraturan, Pasal 1-261 (Ditjen Anggaran Kemenkeu, PDF 670 hlm) | 483 |
| `pmk-107-2024-perubahan.txt` | PMK 107/2024, perubahan atas PMK 62/2023 — hanya badan peraturan (JDIH Kemenkeu, PDF 577 hlm) | 225 |
| `pmk-41-2026-perubahan-kedua.txt` | PMK 41/2026, perubahan kedua atas PMK 62/2023 — hanya badan peraturan (Database Peraturan BPK, PDF 541 hlm) | 177 |

Yang perlu diperhatikan dari batch ini:
- PMK 190/PMK.05/2012 (pembayaran APBN) **tidak dimasukkan** — sudah dicabut; substansinya kini ada di PMK 62/2023 (yang mencabut PMK 210/2022).
- PP 45/2013 dan PMK 113/2012 dimasukkan dalam teks asli, masing-masing disertai file perubahannya (PP 50/2018 dan PMK 119/2023) — jawaban harus memakai versi yang diubah.
- PMK 62/2023, PMK 107/2024, dan PMK 41/2026 hanya berisi badan peraturan; lampiran (format/tabel) tidak diikutkan. PMK 41/2026 adalah perubahan terbaru (berlaku 22 Jun 2026).
- PP 50/2018 dari PDF hasil pindai — ada sedikit kesalahan OCR; verifikasi pasal yang dikutip ke teks resmi.
- UU 15/2006, PP 60/2008, dan PP 8/2006 tidak menyertakan Penjelasan dan (untuk PP 60/2008) Lampiran — berkas sumber JDIH hanya memuat badan peraturan.

Tiap file diawali header `SUMBER:` berisi URL unduhan. Dua cek silang
sudah lolos: uang harian Sumbar Rp380.000 ada dalam satu chunk, dan
tiket Jakarta–Padang ekonomi Rp3.159.000 cocok dengan pagu SBM 2026
yang sudah diverifikasi sebelumnya.

Yang perlu diperhatikan malam ini:
- Perpres 16/2018 dari PDF hasil scan — ada sedikit noise OCR
  (38 karakter pengganti). Jawaban soal pengadaan tetap harus dicek ke
  teks resmi; Perpres 12/2021 sudah ikut di korpus sebagai perubahannya.
- `ingest.py` butuh `OPENROUTER_API_KEY` + DB jalan; embedding default
  `openai/text-embedding-3-small` (1536 dimensi) — pastikan model itu
  tersedia di akun OpenRouter-mu sebelum ingest, karena tabel memakai
  `vector(1536)` dan ingest gagal kalau dimensinya beda.
