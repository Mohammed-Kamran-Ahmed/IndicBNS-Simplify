import os,sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.retriever import HybridRetriever
from src.entities import extract_entities
from src.generate import explain

st.set_page_config(page_title="IndicBNS-Simplify",page_icon="⚖️")
st.title("IndicBNS-Simplify")
st.caption("English • Hindi • Telugu | BNS retrieval + grounded simplification")

@st.cache_resource
def retriever(): return HybridRetriever("artifacts/index")

q=st.text_area("Ask a legal question",placeholder="चोरी करने पर क्या सजा है?")
lang=st.selectbox("Response language",["English","Hindi","Telugu"])

if st.button("Retrieve"):
    r=retriever(); results=r.search(q,k=5)
    for i,x in enumerate(results,1):
        st.markdown(f"**{i}. Section {x['section']} — {x['heading']}**")
        st.caption(f"Hybrid {x['hybrid_score']:.4f} | BM25 {x['bm25_score']:.4f} | BGE-M3 {x['semantic_score']:.4f}")
    best=results[0]; best["entities"]=extract_entities(q,best)
    st.subheader(f"Selected Section {best['section']}")
    st.write(best["text"])
    st.subheader("Entities"); st.json(best["entities"])
    if st.button("Generate grounded explanation"):
        st.write(explain(q,best,lang))

st.divider()
st.caption("Research prototype; verify the official provision for legal use.")
