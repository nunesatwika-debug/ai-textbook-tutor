from src.config import CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS

def chunk_text(text: str, chunk_size_words: int = CHUNK_SIZE_WORDS, overlap_words: int = CHUNK_OVERLAP_WORDS):
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0
    chunk_id = 1

    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words).strip()

        if chunk_text:
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text
            })
            chunk_id += 1

        if end == len(words):
            break

        start = end - overlap_words

    return chunks

def chunk_chapters(chapters: list) -> list:
    all_chunks = []

    for chapter in chapters:
        chapter_chunks = chunk_text(chapter["text"])
        for chunk in chapter_chunks:
            all_chunks.append({
                "chapter_id": chapter["chapter_id"],
                "chapter_title": chapter["chapter_title"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"]
            })

    return all_chunks