import os
import streamlit as st
from src.config import RAW_PDF_DIR, EXTRACTED_DIR, CHUNKS_DIR, FAISS_DIR
from src.utils import save_json, load_json
from src.ingestion.pdf_parser import extract_text_from_pdf
from src.ingestion.chapter_splitter import split_into_chapters
from src.ingestion.chunker import chunk_chapters
from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore
from src.retrieval.chapter_detector import detect_relevant_chapters
from src.retrieval.retriever import Retriever
from src.pruning.context_pruner import prune_context
from src.llm.answer_generator import AnswerGenerator
from src.features.cache_manager import CacheManager

st.set_page_config(page_title="Low-Cost AI Textbook Tutor", layout="wide")
st.title("📘 Low-Cost AI Textbook Tutor with Context Pruning")

uploaded_file = st.file_uploader("Upload textbook PDF", type=["pdf"])
answer_mode = st.selectbox("Answer mode", ["simple", "2-mark", "5-mark"])
question = st.text_area("Ask a question from the textbook")

embedder = Embedder()
cache = CacheManager()

INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")
META_PATH = os.path.join(FAISS_DIR, "metadata.json")
CHUNKS_PATH = os.path.join(CHUNKS_DIR, "chunks.json")
EXTRACTED_PATH = os.path.join(EXTRACTED_DIR, "book.json")

if uploaded_file is not None:
    pdf_path = os.path.join(RAW_PDF_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Process PDF"):
        with st.spinner("Extracting text..."):
            extracted = extract_text_from_pdf(pdf_path)
            save_json(EXTRACTED_PATH, extracted)

        with st.spinner("Splitting chapters..."):
            chapters = split_into_chapters(extracted["full_text"])

        with st.spinner("Chunking..."):
            chunks = chunk_chapters(chapters)
            save_json(CHUNKS_PATH, chunks)

        with st.spinner("Embedding + building index..."):
            texts = [c["text"] for c in chunks]
            embeddings = embedder.embed_texts(texts)

            store = VectorStore(INDEX_PATH, META_PATH)
            store.build(embeddings, chunks)
            store.save()

        st.success("PDF processed successfully.")

if st.button("Ask") and question.strip():
    cached = cache.get(question, answer_mode)
    if cached:
        st.info("Served from cache")
        st.subheader("Answer")
        st.write(cached["answer"])
        st.subheader("Metrics")
        st.json(cached.get("metrics", {}))
    else:
        if not os.path.exists(CHUNKS_PATH) or not os.path.exists(INDEX_PATH):
            st.error("Please upload and process a PDF first.")
        else:
            chunks = load_json(CHUNKS_PATH)

            store = VectorStore(INDEX_PATH, META_PATH)
            store.load()

            relevant_chapters = detect_relevant_chapters(question, chunks)
            query_embedding = embedder.embed_query(question)

            retriever = Retriever(store)
            retrieved = retriever.retrieve(query_embedding)

            pruned = prune_context(retrieved, relevant_chapters)

            generator = AnswerGenerator()
            result = generator.generate_answer(
                pruned_context=pruned["final_context"],
                question=question,
                answer_mode=answer_mode
            )

            original_tokens = result["compression_metrics"]["original_prompt_tokens"]
            compressed_tokens = result["compression_metrics"]["compressed_prompt_tokens"]

            savings = None
            if original_tokens and compressed_tokens and original_tokens > 0:
                savings = round(((original_tokens - compressed_tokens) / original_tokens) * 100, 2)

            metrics = {
                "relevant_chapters": relevant_chapters,
                "retrieved_chunks_count": len(retrieved),
                "pruned_chunks_count": len(pruned["pruned_chunks"]),
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
                "savings_percent": savings
            }

            cache.set(question, answer_mode, {
                "answer": result["answer"],
                "metrics": metrics
            })

            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Answer")
                st.write(result["answer"])

            with col2:
                st.subheader("Metrics")
                st.json(metrics)

            with st.expander("Retrieved Chunks"):
                st.json(retrieved)

            with st.expander("Pruned Context"):
                st.text(pruned["final_context"])

            with st.expander("Compressed Context"):
                st.text(result["compressed_context"])
