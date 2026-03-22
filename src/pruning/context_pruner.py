from src.config import TOP_K_PRUNED, MAX_CONTEXT_CHARS

def prune_context(results: list, relevant_chapters: list, top_k: int = TOP_K_PRUNED, max_chars: int = MAX_CONTEXT_CHARS):
    """
    Pruning rules:
    1. Prefer chunks from detected chapters
    2. Higher similarity first
    3. Avoid duplicate text
    4. Keep only a small total context
    """
    filtered = [r for r in results if r["chapter_title"] in relevant_chapters]

    if not filtered:
        filtered = results

    filtered = sorted(filtered, key=lambda x: x["score"], reverse=True)

    pruned = []
    seen_texts = set()
    current_chars = 0

    for item in filtered:
        normalized = item["text"].strip().lower()
        if normalized in seen_texts:
            continue

        if len(pruned) >= top_k:
            break

        if current_chars + len(item["text"]) > max_chars:
            break

        pruned.append(item)
        seen_texts.add(normalized)
        current_chars += len(item["text"])

    final_context = "\n\n".join(
        f"[{p['chapter_title']} | chunk {p['chunk_id']}]\n{p['text']}"
        for p in pruned
    )

    return {
        "pruned_chunks": pruned,
        "final_context": final_context
    }