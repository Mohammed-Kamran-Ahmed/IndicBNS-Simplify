import json
import pickle
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class HybridRetriever:
    def __init__(self, index_dir):
        p = Path(index_dir)

        meta = json.loads(
            (p / "metadata.json").read_text(encoding="utf-8")
        )

        self.records = meta["records"]
        self.bm25 = pickle.loads((p / "bm25.pkl").read_bytes())
        self.index = faiss.read_index(str(p / "faiss.index"))
        self.model = SentenceTransformer(meta["embedding_model"])

    @staticmethod
    def norm(x):
        x = np.asarray(x, dtype="float32")

        if x.max() - x.min() < 1e-9:
            return np.zeros_like(x)

        return (x - x.min()) / (x.max() - x.min())

    def search(self, query, k=5, alpha=0.55):

        bm = np.asarray(
            self.bm25.get_scores(
                query.lower().split()
            ),
            dtype="float32"
        )

        q = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")

        sem, ids = self.index.search(
            q,
            len(self.records)
        )

        s = np.full(
            len(self.records),
            -1e9,
            dtype="float32"
        )

        s[ids[0]] = sem[0]

        score = (
            (1 - alpha) * self.norm(bm)
            + alpha * self.norm(s)
        )

        order = np.argsort(-score)[:k]

        return [
            {
                **self.records[i],
                "bm25_score": float(bm[i]),
                "semantic_score": float(s[i]),
                "hybrid_score": float(score[i])
            }
            for i in order
        ]