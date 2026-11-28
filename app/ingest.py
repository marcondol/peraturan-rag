"""Ingest dokumen ke pgvector untuk RAG.

Pakai:  python ingest.py [--dir docs-kb/keuangan] [--clear]
  - Membaca *.md / *.txt di --dir (rekursif).
  - Pecah per heading, lalu potong chunk ~1200 karakter (overlap 150)
    supaya satu chunk ≈ satu pasal/bagian, bukan satu file utuh.
  - Embedding via 9router (lihat rag.embed_texts), simpan ke
    tabel rag_documents (id, source, text, embedding).
  - Idempotent: ingest ulang file yang sama menimpa chunk lamanya
    (ON CONFLICT DO UPDATE); --clear menghapus isi tabel dulu.

Korpus malam ini (25 Nov 2026): peraturan keuangan Indonesia untuk
audit — UU 17/2003, UU 1/2004, UU 15/2004, Perpres 16/2018, PMK SBM
32/2025. Ambil teks resminya (peraturan.go.id / jdih), konversi PDF
ke .txt/.md (mis. `pdftotext -layout file.pdf file.txt`), taruh di
docs-kb/keuangan/, lalu jalankan script ini. JANGAN mengetik ulang
atau mengarang isi pasal — sitasi audit harus dari teks resmi.

Butuh env: RAG_DATABASE_URL + NINE_ROUTER_API_KEY (lihat .env.example).
"""

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag import EMBEDDING_DIM, embed_texts, ensure_schema  # noqa: E402

CHUNK_CHARS = 1200
CHUNK_OVERLAP = 150
BATCH = 32


def _split_long(text: str) -> list[str]:
    """Potong teks panjang jadi chunk ~1200 karakter dengan overlap."""
    if len(text) <= CHUNK_CHARS:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_CHARS
        chunk = text[start:end].strip()
        if len(chunk) >= 50:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def chunk_file(path: Path) -> list[dict]:
    """Satu file -> list {id, source, text}. ID dipakai sebagai sitasi."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Pecah per heading (# / ##) — untuk peraturan, satu heading
    # biasanya satu bab/pasal; chunk panjang dipotong lagi di bawah.
    parts = re.split(r"\n(?=#{1,3} )", text)
    docs: list[dict] = []
    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) < 50:
            continue
        # Label pasal di depan chunk, supaya sitasi terbaca di jawaban.
        pasal = re.search(
            r"Pasal\s+\d+[A-Za-z]?(?:\s*ayat\s*\(\d+\))?", part, re.IGNORECASE
        )
        prefix = f"[{pasal.group(0)}] " if pasal else ""
        for j, piece in enumerate(_split_long(part)):
            docs.append(
                {
                    "id": f"{path.stem}#{i}-{j}",
                    "source": path.name,
                    "text": prefix + piece,
                }
            )
    return docs


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest docs-kb ke pgvector")
    parser.add_argument(
        "--dir",
        default=str(Path(__file__).resolve().parent.parent / "docs-kb" / "keuangan"),
        help="folder dokumen (.md/.txt), default docs-kb/keuangan",
    )
    parser.add_argument("--clear", action="store_true", help="kosongkan tabel dulu")
    args = parser.parse_args()

    db_url = os.environ.get("RAG_DATABASE_URL", "")
    if not db_url:
        print("RAG_DATABASE_URL belum diisi (.env)", file=sys.stderr)
        return 1
    if not os.environ.get("NINE_ROUTER_API_KEY"):
        print("NINE_ROUTER_API_KEY belum diisi (.env)", file=sys.stderr)
        return 1

    folder = Path(args.dir)
    files = [
        p
        for p in sorted(folder.rglob("*.md")) + sorted(folder.rglob("*.txt"))
        if p.name.lower() != "readme.md"  # petunjuk, bukan korpus
    ]
    if not files:
        print(
            f"Tidak ada .md/.txt di {folder} — taruh dulu teks peraturan "
            "di sana (lihat docs-kb/keuangan/README.md).",
            file=sys.stderr,
        )
        return 1

    docs: list[dict] = []
    for path in files:
        docs.extend(chunk_file(path))
    print(f"{len(files)} file -> {len(docs)} chunk")

    import psycopg

    with psycopg.connect(db_url) as conn:
        ensure_schema(conn)
        if args.clear:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE rag_documents")
            conn.commit()
            print("Tabel dikosongkan (--clear)")
        for start in range(0, len(docs), BATCH):
            batch = docs[start : start + BATCH]
            vectors = embed_texts([d["text"] for d in batch])
            with conn.cursor() as cur:
                for doc, vec in zip(batch, vectors):
                    cur.execute(
                        "INSERT INTO rag_documents (id, source, text, embedding) "
                        "VALUES (%s, %s, %s, %s::vector) "
                        "ON CONFLICT (id) DO UPDATE SET "
                        "source = EXCLUDED.source, text = EXCLUDED.text, "
                        "embedding = EXCLUDED.embedding",
                        (doc["id"], doc["source"], doc["text"], str(vec)),
                    )
            conn.commit()
            print(f"  {min(start + BATCH, len(docs))}/{len(docs)} chunk tersimpan")
    print(f"Selesai: {len(docs)} chunk di rag_documents (vector({EMBEDDING_DIM}))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
