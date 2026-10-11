# IndicBNS-Simplify

Multilingual BNS section retrieval and grounded simplification for English, Hindi and Telugu.

## Pipeline
Official BNS PDF -> structured sections -> BM25 + BGE-M3 -> hybrid ranking -> entity extraction -> grounded LLM -> Streamlit

## Setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Put the verified official BNS PDF at `data/raw/bns.pdf`.

## Build corpus
```bash
python -m src.build_corpus --pdf data/raw/bns.pdf --out data/processed/bns_sections.jsonl
```

## Build indexes
```bash
python -m src.build_index --corpus data/processed/bns_sections.jsonl --out_dir artifacts/index
```

## Evaluate
Create `data/processed/queries.jsonl` using the example file, replacing gold section IDs with verified labels.

```bash
python -m evaluation.evaluate --queries data/processed/queries.jsonl --index_dir artifacts/index
```

## Run UI
Set `OPENAI_API_KEY`, then:
```bash
streamlit run ui/app.py
```

The LLM is given the retrieved official provision as context and is instructed not to invent legal facts. This is a research prototype, not legal advice.
