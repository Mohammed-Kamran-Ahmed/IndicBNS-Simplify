import argparse
import json

from src.retriever import HybridRetriever


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", required=True)
    parser.add_argument("--index_dir", required=True)
    args = parser.parse_args()

    rows = load(args.queries)
    r = HybridRetriever(args.index_dir)

    for q in rows:
        if q.get("language") == "en":
            continue

        query = q["query"]
        gold = str(q["relevant_sections"][0])

        results = r.search(query, k=10)

        print("\n" + "=" * 80)
        print("QUERY:", query)
        print("GOLD :", gold)

        for i, x in enumerate(results, 1):
            section = str(x["section"])
            marker = "  <-- GOLD" if section == gold else ""

            print(
                f"{i:2}. Section {section} | "
                f"semantic={x['semantic_score']:.4f}"
                f"{marker}"
            )


if __name__ == "__main__":
    main()