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
