import argparse
import json

from src.retriever import HybridRetriever


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def hit_at_k(pred, gold, k):
    return float(gold in pred[:k])


def mrr(pred, gold):
    return (
        1 / (pred.index(gold) + 1)
        if gold in pred
        else 0.0
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--queries", required=True)
    parser.add_argument("--index_dir", required=True)

    args = parser.parse_args()

    queries = load(args.queries)
    retriever = HybridRetriever(args.index_dir)

    alphas = [0.0, 0.25, 0.50, 0.55, 0.75, 1.0]

    print("\nALPHA EXPERIMENT")
    print("=" * 70)

    for alpha in alphas:

        results = {
            "en": [],
            "hi": [],
            "te": []
        }

        for q in queries:

            retrieved = retriever.search(
                q["query"],
                k=5,
                alpha=alpha
            )

            # hybrid_score is the score calculated using this alpha
            retrieved = sorted(
                retrieved,
                key=lambda x: x["hybrid_score"],
                reverse=True
            )

            pred = [
                str(x["section"])
                for x in retrieved
            ]

            gold = str(
                q["relevant_sections"][0]
            )

            language = q.get(
                "language",
                "unknown"
            )

            results.setdefault(
                language,
                []
            )

            results[language].append({
                "hit1": hit_at_k(pred, gold, 1),
                "hit3": hit_at_k(pred, gold, 3),
                "hit5": hit_at_k(pred, gold, 5),
                "mrr": mrr(pred, gold)
            })

        print(f"\nAlpha = {alpha}")

        for language, values in results.items():

            if not values:
                continue

            n = len(values)

            hit1 = sum(
                x["hit1"] for x in values
            ) / n

            hit3 = sum(
                x["hit3"] for x in values
            ) / n

            hit5 = sum(
                x["hit5"] for x in values
            ) / n

            mrr_score = sum(
                x["mrr"] for x in values
            ) / n

            print(
                f"{language}: "
                f"Hit@1={hit1:.3f}, "
                f"Hit@3={hit3:.3f}, "
                f"Hit@5={hit5:.3f}, "
                f"MRR={mrr_score:.3f}"
            )


if __name__ == "__main__":
    main()