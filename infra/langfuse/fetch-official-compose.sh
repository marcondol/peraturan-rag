#!/usr/bin/env bash
# Ambil docker-compose.yml RESMI Langfuse (v3) + generate .env dengan
# secret acak. Jangan tulis compose Langfuse sendiri — env var berubah
# antar minor release. Jalankan dari repo root: bash infra/langfuse/fetch-official-compose.sh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

curl -fsSLO https://raw.githubusercontent.com/langfuse/langfuse/main/docker-compose.yml

if grep -q CHANGEME docker-compose.yml; then
  echo "OK: compose resmi terunduh; placeholder CHANGEME masih ada (wajar)."
fi

if [ ! -f .env ]; then
  {
    echo "NEXTAUTH_SECRET=$(openssl rand -hex 32)"
    echo "SALT=$(openssl rand -hex 32)"
    echo "ENCRYPTION_KEY=$(openssl rand -hex 32)"
    echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)"
    echo "CLICKHOUSE_PASSWORD=$(openssl rand -hex 16)"
    echo "MINIO_ROOT_PASSWORD=$(openssl rand -hex 16)"
    echo "LANGFUSE_SALT_placeholder=isi-dari-env-di-atas"
  } > .env
  chmod 600 .env
  echo "OK: .env dibuat (600). Cocokkan nilai-nilainya ke compose bila perlu."
else
  echo "SKIP: .env sudah ada, tidak ditimpa."
fi

echo "Lanjut: docker compose up -d  (butuh ~4 GB RAM / 2-4 vCPU)"
echo "Lalu buka http://localhost:3000, buat akun admin, ambil API keys"
echo "dan isi LANGFUSE_* di repo root .env."
