import os
from dotenv import load_dotenv

load_dotenv()

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data folders
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_PDF_DIR = os.path.join(DATA_DIR, "raw_pdfs")
EXTRACTED_DIR = os.path.join(DATA_DIR, "extracted")
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")
FAISS_DIR = os.path.join(DATA_DIR, "faiss_index")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# Create folders automatically
for folder in [DATA_DIR, RAW_PDF_DIR, EXTRACTED_DIR, CHUNKS_DIR, FAISS_DIR, CACHE_DIR]:
    os.makedirs(folder, exist_ok=True)

# API keys
SCALEDOWN_API_KEY = os.getenv("SCALEDOWN_API_KEY", "")

# ScaleDown compression endpoint
SCALEDOWN_COMPRESS_URL = "https://api.scaledown.xyz/compress/raw/"

# Optional generation settings
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

# Embeddings
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Chunking and retrieval settings
CHUNK_SIZE_WORDS = 350
CHUNK_OVERLAP_WORDS = 60
TOP_K_RETRIEVAL = 10
TOP_K_PRUNED = 4
MAX_CONTEXT_CHARS = 6000
