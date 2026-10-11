import argparse
import json

from src.retriever import HybridRetriever


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def print_results(title, results):
    print(f"\n{title}")

    for rank, result in enumerate(results, start=1):
        print(
            f"  #{rank} "
            f"Section {result['section']} | "
            f"Hybrid={result['hybrid_score']:.4f} | "
            f"BM25={result['bm25_score']:.4f} | "
            f"Semantic={result['semantic_score']:.4f}"
        )
        print(f"      {result['heading']}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--queries",
        required=True
    )

    parser.add_argument(
        "--index_dir",
        required=True
    )

    args = parser.parse_args()

    rows = load(args.queries)
    retriever = HybridRetriever(args.index_dir)

    for q in rows:

        query = q["query"]
        language = q.get("language", "unknown")
        gold = str(q["relevant_sections"][0])

        results = retriever.search(query, k=5)

        # Rankings for each method
        bm25_results = sorted(
            results,
            key=lambda x: x["bm25_score"],
            reverse=True
        )

        semantic_results = sorted(
            results,
            key=lambda x: x["semantic_score"],
            reverse=True
        )

        hybrid_results = sorted(
            results,
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        # Check whether each method got the correct section at #1
        bm25_top = str(bm25_results[0]["section"])
        semantic_top = str(semantic_results[0]["section"])
        hybrid_top = str(hybrid_results[0]["section"])

        # Only show queries where at least one method failed
        if (
            bm25_top != gold
            or semantic_top != gold
            or hybrid_top != gold
        ):

            print("\n" + "=" * 90)
            print(f"QUERY    : {query}")
            print(f"LANGUAGE : {language}")
            print(f"GOLD     : Section {gold}")
            print("=" * 90)

            print_results("BM25 TOP 5", bm25_results)

            print_results("BGE-M3 TOP 5", semantic_results)

            print_results("HYBRID TOP 5", hybrid_results)


if __name__ == "__main__":
    main()