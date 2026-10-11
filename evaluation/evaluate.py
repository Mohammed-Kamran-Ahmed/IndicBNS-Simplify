import argparse
import json
from collections import defaultdict

from src.retriever import HybridRetriever
from .metrics import hit_at_k, mrr


def load(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", required=True)
    ap.add_argument("--index_dir", required=True)

    a = ap.parse_args()

    rows = load(a.queries)
    r = HybridRetriever(a.index_dir)

    output = {}

    for method in ["bm25", "bge-m3", "hybrid"]:

        by = defaultdict(list)

        for q in rows:

            res = r.search(q["query"], k=5)

            key = {
                "bm25": "bm25_score",
                "bge-m3": "semantic_score",
                "hybrid": "hybrid_score"
            }[method]

            res = sorted(
                res,
                key=lambda x: x[key],
                reverse=True
            )

            pred = [str(x["section"]) for x in res]

            # Ground-truth sections
            gold = str(q["relevant_sections"][0])

            by[q.get("language", "unknown")].append([
                hit_at_k(pred, gold, 1),
                hit_at_k(pred, gold, 3),
                hit_at_k(pred, gold, 5),
                mrr(pred, gold)
            ])

        output[method] = {}

        for lang, vals in by.items():

            n = len(vals)

            output[method][lang] = {
                "Hit@1": sum(x[0] for x in vals) / n,
                "Hit@3": sum(x[1] for x in vals) / n,
                "Hit@5": sum(x[2] for x in vals) / n,
                "MRR": sum(x[3] for x in vals) / n,
                "n": n
            }

    print(json.dumps(
        output,
        indent=2,
        ensure_ascii=False
    ))


if __name__ == "__main__":
    main()