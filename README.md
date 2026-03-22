# 📘 Low-Cost AI Textbook Tutor with Context Pruning

## 🚀 Overview

Personalized AI tutors are powerful but expensive to run, especially in low-resource environments like rural India.
This project builds an **intelligent, cost-efficient tutoring system** that can ingest full textbooks and answer questions while minimizing API usage and latency.

The core innovation is **Context Pruning**, where only the most relevant parts of a textbook are sent to the language model — drastically reducing cost and improving speed.

---

## 🎯 Problem Statement

* Large textbook PDFs must be processed efficiently
* Avoid sending entire documents to LLMs for every query
* Reduce API cost and data transfer
* Provide curriculum-aligned answers

---

## 💡 Solution

We implement a **Hybrid RAG (Retrieval-Augmented Generation) system** with:

* 📄 One-time PDF ingestion
* 🔍 Semantic retrieval using FAISS
* ✂️ Context pruning (main innovation)
* 🧠 Query-aware compression using ScaleDown
* 🤖 Final answer generation using OpenRouter / Groq
* ⚡ Caching for repeated queries

---

## 🏗️ Architecture

```
PDF → Text Extraction → Chapter Split → Chunking → Embeddings → FAISS Index

User Query
   ↓
Chapter Detection
   ↓
Top-K Retrieval (10 chunks)
   ↓
Context Pruning (→ 3–4 chunks)
   ↓
ScaleDown Compression
   ↓
LLM (OpenRouter / Groq)
   ↓
Final Answer
```

---

## 🔥 Key Features

### ✅ Context Pruning (Core Innovation)

* Reduces irrelevant textbook content
* Keeps only top 3–4 most relevant chunks
* Maintains answer quality while lowering cost

---

### ✅ Token & Cost Optimization

* 60–80% reduction in tokens sent to LLM
* Faster response times
* Lower API usage

---

### ✅ Smart Retrieval

* FAISS-based semantic search
* Chapter-aware filtering

---

### ✅ Query-Aware Compression (ScaleDown)

* Compresses context before sending to LLM
* Further reduces token usage

---

### ✅ Answer Modes

* Simple explanation
* 2-mark answer (concise)
* 5-mark answer (detailed)

---

### ✅ Caching System

* Stores previous answers
* Avoids repeated API calls
* Improves performance

---

## 🛠️ Tech Stack

| Component           | Technology           |
| ------------------- | -------------------- |
| Backend             | Python               |
| UI                  | Streamlit            |
| PDF Parsing         | PyMuPDF              |
| Embeddings          | SentenceTransformers |
| Vector DB           | FAISS                |
| Context Compression | ScaleDown API        |
| LLM                 | OpenRouter / Groq    |
| Environment         | Python venv          |

---

## 📂 Project Structure

```
ai-textbook-tutor/
│
├── app.py
├── requirements.txt
├── .env
│
├── data/
│   ├── raw_pdfs/
│   ├── extracted/
│   ├── chunks/
│   ├── faiss_index/
│   └── cache/
│
└── src/
    ├── config.py
    ├── utils.py
    │
    ├── ingestion/
    ├── retrieval/
    ├── pruning/
    ├── llm/
    └── features/
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/nunesatwika-debug/ai-textbook-tutor.git
cd ai-textbook-tutor
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Environment Variables

Create `.env` file:

```env
SCALEDOWN_API_KEY=your_scaledown_key

LLM_API_KEY=your_openrouter_or_groq_key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=deepseek/deepseek-chat
```

---

### 5️⃣ Run Application

```bash
python -m streamlit run app.py
```

---

## 📊 Example Output

| Metric           | Baseline RAG | Our System     |
| ---------------- | ------------ | -------------- |
| Retrieved Chunks | 10           | 10             |
| Sent to LLM      | 10           | 3–4            |
| Token Usage      | High         | Low            |
| Cost             | High         | Reduced (~70%) |
| Latency          | Slower       | Faster         |

---

## 🧠 Key Innovation

> Instead of sending entire textbook context, we **intelligently prune and compress context**, ensuring:

* Lower cost per query
* Faster responses
* Better relevance

---

## 🌍 Impact

This system enables:

* Affordable AI tutoring
* Low-bandwidth usage
* Better accessibility in rural areas
* Scalable education solutions

---

## 🚧 Future Improvements

* 📊 Weak-area tracking for personalization
* 🌐 Multilingual support (English + Telugu/Hindi)
* 🧪 Quiz generation (MCQs)
* 📱 Mobile-friendly UI
* 🧠 Offline fallback with local models

---

## 👨‍💻 Team

* Built as part of a collaborative project
* Focused on efficient AI systems for education

---

## ⭐ Final Note

> This project demonstrates how **smart engineering (context pruning + compression)** can make advanced AI systems **affordable and scalable**.

---

✨ If you like this project, consider starring the repo!
