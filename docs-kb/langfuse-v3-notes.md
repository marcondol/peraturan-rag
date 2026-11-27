# Catatan Langfuse v3 (dokumen contoh untuk retrieval pertama)

## Komponen

Langfuse v3 self-hosted menjalankan enam container: web UI (port 3000),
async worker, PostgreSQL untuk metadata, ClickHouse untuk analitik trace,
Redis untuk antrean, dan MinIO/S3 untuk blob storage. Ini berubah besar
dari v2 yang hanya butuh PostgreSQL.

## Kebutuhan hardware

Untuk beban homelab, siapkan minimal 4 GB RAM dan 2 vCPU; ClickHouse
memakan memori paling besar dan akan OOM-killed di VPS 2 GB. Disk mulai
dari 100 GB; ClickHouse tumbuh kira-kira 1–2 GB per satu juta trace,
tergantung ukuran prompt dan completion.

## Cara deploy yang benar

Pakai docker-compose.yml resmi dari repositori Langfuse, jangan tulis
sendiri — variabel environment berubah antar minor release. Generate
semua secret dengan `openssl rand -hex` (bukan base64, karena karakter
`/`, `+`, `=` merusak URL koneksi PostgreSQL). Web dan worker harus
berbagi ENCRYPTION_KEY, SALT, dan NEXTAUTH_SECRET yang sama.

## Versi

Per Oktober 2026, Langfuse 3.224.2 dipasangkan dengan ClickHouse
26.5.x. Langfuse v4 mengubah model data ClickHouse — jangan upgrade
tanpa verifikasi.
