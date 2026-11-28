"""Retrieval: pgvector bila RAG_DATABASE_URL tersedia, fallback keyword
atas docs-kb/ bila belum ada DB. Fallback ini menjaga demo pertama
tetap jalan.

Embedding lewat 9router (DIPUTUSKAN 27 Nov 2026, ganti OpenRouter):
EMBEDDING_MODEL default nvidia/nemotron-3.5-embed-8b (4096 dimensi),
token dari NINE_ROUTER_API_KEY, base https://9router.marcondol.site/v1.
Terverifikasi 27 Nov 2026: POST /v1/embeddings HTTP 200, router
mengembalikan vektor 4096 dimensi (model di-echo sebagai
nvidia/nemotron-3.5-embed-8b; bentuk ganda nvidia/nvidia/... juga
diterima). Tabel rag_documents memakai vector(4096) — bila ganti
model embedding ke dimensi lain, hapus tabelnya dulu
(DROP TABLE rag_documents) lalu ingest ulang. `input_type` dikirim
("passage" untuk dokumen, "query" untuk pertanyaan) karena panggilan
yang terverifikasi memakainya; bila router menolaknya, hapus
extra_body dan coba lagi. Format dokumen: {"id": str, "text": str}.
ID dipakai sebagai sitasi di jawaban dan dicatat di trace Langfuse.
"""

import os
import re
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "docs-kb"
EMBEDDING_DIM = 4096


def _load_kb_files() -> list[dict]:
    docs = []
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        # Satu file = satu dokumen; pecah per heading bila file panjang.
        chunks = re.split(r"\n## ", text)
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if len(chunk) < 50:
                continue
            docs.append({"id": f"{path.stem}#{i}", "text": chunk})
    return docs


def _keyword_retrieve(query: str, docs: list[dict], top_k: int) -> list[dict]:
    terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    scored = []
    for doc in docs:
        hay = doc["text"].lower()
        score = sum(hay.count(t) for t in terms)
        scored.append((score, doc))
    scored.sort(key=lambda s: -s[0])
    top = [d for s, d in scored[:top_k] if s > 0]
    return top or scored[:1]  # minimal satu konteks agar prompt terisi


def embed_texts(texts: list[str], input_type: str = "passage") -> list[list[float]]:
    """Embedding via 9router (OpenAI-compatible). Satu key dengan LLM."""
    from openai import OpenAI

    api_key = os.environ.get("NINE_ROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("NINE_ROUTER_API_KEY belum diisi (.env)")
    model = os.environ.get("EMBEDDING_MODEL", "nvidia/nemotron-3.5-embed-8b")
    client = OpenAI(base_url="https://9router.marcondol.site/v1", api_key=api_key)
    resp = client.embeddings.create(
        input=texts, model=model, extra_body={"input_type": input_type}
    )
    vectors = [list(item.embedding) for item in resp.data]
    if vectors and len(vectors[0]) != EMBEDDING_DIM:
        raise RuntimeError(
            f"Embedding model {model} berdimensi {len(vectors[0])}, "
            f"sedangkan tabel memakai vector({EMBEDDING_DIM}). "
            "Pakai model 4096-dimensi atau DROP TABLE rag_documents dulu."
        )
    return vectors


def ensure_schema(conn) -> None:
    """Buat ekstensi + tabel bila belum ada. Dipakai ingest.py juga."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute(
            f"""CREATE TABLE IF NOT EXISTS rag_documents (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding vector({EMBEDDING_DIM})
            )"""
        )
    conn.commit()


def _pgvector_retrieve(query: str, top_k: int) -> list[dict] | None:
    """Embedding query -> SELECT ... ORDER BY embedding <=> $1 LIMIT top_k.
    Mengembalikan None bila DB/tabel/kunci belum siap, supaya fallback
    keyword yang jalan (bukan error 500 di /ask)."""
    db_url = os.environ.get("RAG_DATABASE_URL", "")
    if not db_url:
        return None
    try:
        import psycopg

        query_vec = embed_texts([query], input_type="query")[0]
        with psycopg.connect(db_url) as conn:
            ensure_schema(conn)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, text FROM rag_documents "
                    "ORDER BY embedding <=> %s::vector LIMIT %s",
                    (str(query_vec), top_k),
                )
                rows = cur.fetchall()
        return [{"id": row[0], "text": row[1]} for row in rows] or None
    except Exception:
        return None


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    if os.environ.get("RAG_DATABASE_URL"):
        hits = _pgvector_retrieve(query, top_k)
        if hits:
            return hits
    return _keyword_retrieve(query, _load_kb_files(), top_k)
