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


st.set_page_config(
    page_title="AI Textbook Tutor",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)


def inject_custom_css():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
        }

        .main > div {
            padding-top: 1rem;
        }

        .hero-card {
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 55%, #60a5fa 100%);
            padding: 2rem;
            border-radius: 24px;
            color: white;
            box-shadow: 0 20px 50px rgba(37, 99, 235, 0.18);
            margin-bottom: 1.2rem;
        }

        .hero-title {
            font-size: 2.15rem;
            font-weight: 800;
            margin-bottom: 0.4rem;
            line-height: 1.2;
            color: white;
        }

        .hero-subtitle {
            font-size: 1rem;
            line-height: 1.6;
            color: rgba(255,255,255,0.96);
        }

        .badge-row {
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }

        .badge {
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.18);
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
            color: white;
        }

        .section-title {
            font-size: 1.12rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 0.2rem;
            margin-bottom: 0.7rem;
        }

        .subtle-card {
            background: rgba(255,255,255,0.82);
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 1rem 1rem 0.9rem 1rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
            margin-bottom: 1rem;
        }

        .metric-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            text-align: center;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            color: #0f172a;
            font-size: 1.45rem;
            font-weight: 800;
        }

        .answer-card {
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-left: 7px solid #2563eb;
            border-radius: 20px;
            padding: 1.2rem;
            box-shadow: 0 12px 30px rgba(37, 99, 235, 0.07);
        }

        .answer-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.7rem;
        }

        .answer-text {
            color: #334155;
            line-height: 1.8;
            font-size: 1rem;
        }

        .chunk-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 1rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
        }

        .chunk-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.6rem;
            flex-wrap: wrap;
        }

        .chunk-title {
            font-weight: 800;
            color: #1e293b;
            font-size: 1rem;
        }

        .chunk-score {
            background: #eff6ff;
            color: #1d4ed8;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .chunk-body {
            color: #334155;
            line-height: 1.65;
        }

        .sidebar-note {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 1rem;
            color: #334155;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .status-ok {
            color: #15803d;
            font-weight: 700;
        }

        .status-warn {
            color: #b45309;
            font-weight: 700;
        }

        .small-muted {
            color: #64748b;
            font-size: 0.88rem;
        }

        .info-card-title {
            color: #0f172a;
            font-size: 1.05rem;
            font-weight: 800;
            margin-bottom: 0.6rem;
        }

        .info-card-text {
            color: #334155;
            line-height: 1.7;
            font-size: 0.98rem;
        }

        .stButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 0.75rem 1rem;
            font-weight: 700;
            border: none;
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18);
        }

        .stButton > button:hover {
            filter: brightness(1.03);
        }

        div[data-testid="stFileUploader"] {
            background: #ffffff;
            border-radius: 16px;
            padding: 0.35rem;
            border: 1px solid #e2e8f0;
        }

        div[data-baseweb="select"] > div {
            border-radius: 14px !important;
        }

        textarea {
            border-radius: 14px !important;
        }

        label, .stMarkdown, .stCaption, p, span, div {
            color: inherit;
        }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def get_embedder():
    return Embedder()


@st.cache_resource
def get_cache_manager():
    return CacheManager()


def ensure_session_state():
    defaults = {
        "processed_ready": False,
        "processed_filename": None,
        "last_result": None,
        "book_stats": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_hero():
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">📘 AI Textbook Tutor</div>
        <div class="hero-subtitle">
            Upload your textbook, process it into smart learning chunks, and ask questions in a
            student-friendly way. Built for revision, exam preparation, and faster understanding.
        </div>
        <div class="badge-row">
            <div class="badge">PDF Ingestion</div>
            <div class="badge">FAISS Retrieval</div>
            <div class="badge">Context Pruning</div>
            <div class="badge">ScaleDown Compression</div>
            <div class="badge">Exam-Style Answers</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_chunk_cards(chunks):
    if not chunks:
        st.info("No retrieved chunks to display.")
        return

    for item in chunks:
        chapter_title = item.get("chapter_title", "Unknown Chapter")
        chunk_id = item.get("chunk_id", "-")
        score = item.get("score")
        text = item.get("text", "")

        score_text = f"{score:.4f}" if isinstance(score, (float, int)) else "N/A"

        st.markdown(
            f"""
            <div class="chunk-card">
                <div class="chunk-header">
                    <div class="chunk-title">{chapter_title} · Chunk {chunk_id}</div>
                    <div class="chunk-score">Score: {score_text}</div>
                </div>
                <div class="chunk-body">{text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def compute_metrics(result, retrieved, pruned, relevant_chapters):
    original_tokens = result["compression_metrics"].get("original_prompt_tokens")
    compressed_tokens = result["compression_metrics"].get("compressed_prompt_tokens")

    savings = 0
    if (
        isinstance(original_tokens, (int, float))
        and isinstance(compressed_tokens, (int, float))
        and original_tokens > 0
    ):
        savings = round(((original_tokens - compressed_tokens) / original_tokens) * 100, 2)

    return {
        "relevant_chapters": relevant_chapters,
        "retrieved_chunks_count": len(retrieved),
        "pruned_chunks_count": len(pruned["pruned_chunks"]),
        "original_tokens": original_tokens if original_tokens is not None else 0,
        "compressed_tokens": compressed_tokens if compressed_tokens is not None else 0,
        "savings_percent": savings,
    }


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎓 Tutor Controls")

        st.markdown('<div class="section-title">Answer Style</div>', unsafe_allow_html=True)
        answer_mode = st.selectbox(
            "Choose how the answer should be written",
            ["simple", "2-mark", "5-mark"],
            help="Simple = student-friendly explanation, 2-mark = concise exam answer, 5-mark = structured exam response."
        )

        st.markdown('<div class="section-title">Study Guide</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sidebar-note">
            <b>Suggested workflow</b><br><br>
            1. Upload a textbook PDF<br>
            2. Click <b>Process PDF</b><br>
            3. Ask a chapter-based question<br>
            4. Review answer, sources, and compression metrics
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">Current Status</div>', unsafe_allow_html=True)
        if st.session_state.processed_ready:
            st.markdown(
                f"<div class='status-ok'>✅ Ready</div><div class='small-muted'>Processed book: {st.session_state.processed_filename}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='status-warn'>⏳ Waiting for textbook processing</div>",
                unsafe_allow_html=True
            )

    return answer_mode


inject_custom_css()
ensure_session_state()

embedder = get_embedder()
cache = get_cache_manager()

INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")
META_PATH = os.path.join(FAISS_DIR, "metadata.json")
CHUNKS_PATH = os.path.join(CHUNKS_DIR, "chunks.json")
EXTRACTED_PATH = os.path.join(EXTRACTED_DIR, "book.json")

render_hero()
answer_mode = render_sidebar()

left_col, right_col = st.columns([1.1, 1.4], gap="large")

with left_col:
    st.markdown('<div class="section-title">📂 Upload Textbook</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload textbook PDF", type=["pdf"], label_visibility="collapsed")

    process_clicked = st.button("⚙️ Process PDF")

    if uploaded_file is not None:
        st.caption(f"Selected file: **{uploaded_file.name}**")

    if uploaded_file is not None and process_clicked:
        pdf_path = os.path.join(RAW_PDF_DIR, uploaded_file.name)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        progress = st.progress(0, text="Starting pipeline...")
        status_box = st.empty()

        try:
            status_box.info("Step 1/4 — Extracting text from PDF")
            extracted = extract_text_from_pdf(pdf_path)
            save_json(EXTRACTED_PATH, extracted)
            progress.progress(25, text="Text extracted")

            status_box.info("Step 2/4 — Splitting into chapters")
            chapters = split_into_chapters(extracted["full_text"])
            progress.progress(50, text="Chapters detected")

            status_box.info("Step 3/4 — Chunking chapters")
            chunks = chunk_chapters(chapters)
            save_json(CHUNKS_PATH, chunks)
            progress.progress(75, text="Chunks created")

            status_box.info("Step 4/4 — Creating embeddings and FAISS index")
            texts = [c["text"] for c in chunks]
            embeddings = embedder.embed_texts(texts)

            store = VectorStore(INDEX_PATH, META_PATH)
            store.build(embeddings, chunks)
            store.save()

            progress.progress(100, text="Processing complete")
            status_box.success("✅ Your textbook is ready for questions.")

            st.session_state.processed_ready = True
            st.session_state.processed_filename = uploaded_file.name
            st.session_state.book_stats = {
                "pages": extracted.get("num_pages", 0),
                "chapters": len(chapters),
                "chunks": len(chunks)
            }

        except Exception as e:
            st.session_state.processed_ready = False
            status_box.error(f"Processing failed: {e}")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">❓ Ask a Question</div>', unsafe_allow_html=True)
    question = st.text_area(
        "Enter your textbook question",
        height=130,
        placeholder="Example: Explain the difference between mitosis and meiosis in simple terms.",
        label_visibility="collapsed"
    )

    ask_clicked = st.button("🚀 Generate Answer")


with right_col:
    st.markdown('<div class="section-title">📊 Book & Session Overview</div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric_card(
            "Pages",
            st.session_state.book_stats["pages"] if st.session_state.book_stats else "—"
        )
    with m2:
        render_metric_card(
            "Chapters",
            st.session_state.book_stats["chapters"] if st.session_state.book_stats else "—"
        )
    with m3:
        render_metric_card(
            "Chunks",
            st.session_state.book_stats["chunks"] if st.session_state.book_stats else "—"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="subtle-card">
        <div class="info-card-title">💡 Why this helps students</div>
        <div class="info-card-text">
            • Get answers grounded in your uploaded textbook<br>
            • Choose between simple explanation and exam-style responses<br>
            • Review retrieved learning context for better trust<br>
            • Save prompt cost through context compression
        </div>
    </div>
    """, unsafe_allow_html=True)


if ask_clicked:
    if not question.strip():
        st.warning("Please enter a question first.")
    elif not os.path.exists(CHUNKS_PATH) or not os.path.exists(INDEX_PATH):
        st.error("Please upload and process a PDF first.")
    else:
        cached = cache.get(question, answer_mode)

        if cached:
            st.session_state.last_result = {
                "answer": cached.get("answer"),
                "metrics": cached.get("metrics", {}),
                "retrieved": [],
                "pruned_context": None,
                "compressed_context": None,
                "cache_hit": True
            }
        else:
            with st.spinner("Thinking through your textbook..."):
                try:
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

                    metrics = compute_metrics(result, retrieved, pruned, relevant_chapters)

                    cache.set(question, answer_mode, {
                        "answer": result["answer"],
                        "metrics": metrics
                    })

                    st.session_state.last_result = {
                        "answer": result["answer"],
                        "metrics": metrics,
                        "retrieved": retrieved,
                        "pruned_context": pruned["final_context"],
                        "compressed_context": result["compressed_context"],
                        "cache_hit": False
                    }

                except Exception as e:
                    st.error(f"Answer generation failed: {e}")


if st.session_state.last_result:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Results</div>', unsafe_allow_html=True)

    result = st.session_state.last_result
    metrics = result.get("metrics", {})

    top1, top2, top3, top4 = st.columns(4)
    with top1:
        render_metric_card("Retrieved", metrics.get("retrieved_chunks_count", 0))
    with top2:
        render_metric_card("Pruned", metrics.get("pruned_chunks_count", 0))
    with top3:
        render_metric_card("Orig. Tokens", metrics.get("original_tokens", 0))
    with top4:
        render_metric_card("Savings %", f"{metrics.get('savings_percent', 0)}%")

    if result.get("cache_hit"):
        st.info("⚡ This answer was served from cache for faster response.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Answer",
        "Retrieved Chunks",
        "Pruned Context",
        "Compressed Context"
    ])

    with tab1:
        st.markdown(
            f"""
            <div class="answer-card">
                <div class="answer-title">Generated Answer</div>
                <div class="answer-text">{result.get("answer", "")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        relevant_chapters = metrics.get("relevant_chapters", [])
        if relevant_chapters:
            st.markdown("#### Relevant Chapters")
            st.write(", ".join(relevant_chapters))

    with tab2:
        render_chunk_cards(result.get("retrieved", []))

    with tab3:
        pruned_context = result.get("pruned_context")
        if pruned_context:
            st.text_area("Pruned Context", pruned_context, height=350)
        else:
            st.info("Pruned context is not available for cached results.")

    with tab4:
        compressed_context = result.get("compressed_context")
        if compressed_context:
            st.text_area("Compressed Context", compressed_context, height=350)
        else:
            st.info("Compressed context is not available for cached results.")