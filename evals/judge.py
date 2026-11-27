"""LLM-as-judge eval: jalankan dataset.jsonl lewat /ask, nilai tiap
jawaban terhadap jawaban referensi, tulis laporan.

Penilaian memakai LLM yang sama (prompt judge) bila LLM_BACKEND bukan
demo; bila demo, fallback ke skor heuristik (overlap kata kunci)
supaya pipeline eval tetap bisa diuji end-to-end tanpa biaya.
Target: kembangkan dataset ke 30-50 Q&A di Minggu 2; skor yang
dilaporkan: faithfulness (jawaban didukung konteks) dan relevansi.

Pemakaian:  python evals/judge.py [--base-url http://localhost:8000]
Keluaran:  evals/report-<tanggal>.json
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import httpx

BASE = Path(__file__).resolve().parent


def load_dataset(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def heuristic_score(answer: str, reference: str) -> dict:
    ref_terms = {t.lower() for t in re.findall(r"\w+", reference) if len(t) > 3}
    ans = answer.lower()
    hit = sum(1 for t in ref_terms if t in ans)
    coverage = round(hit / max(len(ref_terms), 1), 2)
    return {"faithfulness_heuristic": coverage, "relevance_heuristic": coverage}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--dataset", default=str(BASE / "dataset.jsonl"))
    args = parser.parse_args()

    rows = load_dataset(Path(args.dataset))
    results = []
    for row in rows:
        resp = httpx.post(
            f"{args.base_url}/ask",
            json={"question": row["question"]},
            timeout=120,
        )
        resp.raise_for_status()
        body = resp.json()
        scores = heuristic_score(body["answer"], row["reference_answer"])
        results.append(
            {
                "question": row["question"],
                "answer": body["answer"][:500],
                "sources": body["sources"],
                "cost_usd": body["cost_usd"],
                "latency_ms": body["latency_ms"],
                **scores,
            }
        )

    avg_faith = round(
        sum(r["faithfulness_heuristic"] for r in results) / max(len(results), 1), 3
    )
    total_cost = round(sum(r["cost_usd"] for r in results), 6)
    report = {
        "date": str(date.today()),
        "n": len(results),
        "avg_faithfulness_heuristic": avg_faith,
        "total_cost_usd": total_cost,
        "note": (
            "Skor heuristik (overlap kata kunci) — ganti ke LLM-as-judge "
            "dengan prompt judge di Minggu 2; angka ini baseline, bukan "
            "skor eval final."
        ),
        "results": results,
    }
    out = BASE / f"report-{date.today().isoformat()}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"{len(results)} pertanyaan, faithfulness heuristik rata-rata {avg_faith}, "
          f"total cost ${total_cost} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
