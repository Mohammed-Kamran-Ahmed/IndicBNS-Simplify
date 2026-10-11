from src.retriever import HybridRetriever


retriever = HybridRetriever("artifacts/index")


queries = [
    "what is the punishment for theft?",
    "चोरी करने पर क्या सजा है?",
    "criminal intimidation",
    "dowry death",
]


for query in queries:

    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = retriever.search(
        query,
        k=5
    )

    for rank, result in enumerate(results, start=1):

        print(
            f"\n#{rank}"
            f"  Section: {result['section']}"
            f"\nHeading: {result['heading']}"
            f"\nBM25: {result['bm25_score']:.4f}"
            f"\nSemantic: {result['semantic_score']:.4f}"
            f"\nHybrid: {result['hybrid_score']:.4f}"
        )