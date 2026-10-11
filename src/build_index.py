import argparse,json,pickle
from pathlib import Path
import faiss,numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from .config import EMBEDDING_MODEL

def load(p):
    with open(p,encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",required=True); ap.add_argument("--out_dir",required=True)
    ap.add_argument("--model",default=EMBEDDING_MODEL); a=ap.parse_args()
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    rows=load(a.corpus)
      # texts=[f"section {r['section']} {r['heading']} {r['text']}" for r in rows]
    texts = [
    r.get(
        "retrieval_text",
        f"section {r['section']} {r['heading']} {r['text']}"
    )
    for r in rows
]
    bm25=BM25Okapi([x.lower().split() for x in texts])
    (out/"bm25.pkl").write_bytes(pickle.dumps(bm25))

    model=SentenceTransformer(a.model)
    emb=model.encode(texts,batch_size=16,normalize_embeddings=True,
                     convert_to_numpy=True,show_progress_bar=True).astype("float32")
    np.save(out/"embeddings.npy",emb)
    index=faiss.IndexFlatIP(emb.shape[1]); index.add(emb)
    faiss.write_index(index,str(out/"faiss.index"))
    (out/"metadata.json").write_text(json.dumps(
        {"embedding_model":a.model,"records":rows},ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Indexed {len(rows)} sections.")

if __name__=="__main__": main()
