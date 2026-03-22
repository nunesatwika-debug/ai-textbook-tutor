def detect_relevant_chapters(query: str, all_chunks: list, top_n: int = 2) -> list:
    """
    Simple keyword-based chapter detector.
    Later you can upgrade to embedding similarity on chapter titles.
    """
    query_words = set(word.lower() for word in query.split())

    chapter_scores = {}

    for chunk in all_chunks:
        title = chunk["chapter_title"]
        title_words = set(word.lower() for word in title.split())
        overlap = len(query_words.intersection(title_words))

        if title not in chapter_scores:
            chapter_scores[title] = 0

        chapter_scores[title] += overlap

    ranked = sorted(chapter_scores.items(), key=lambda x: x[1], reverse=True)
    return [title for title, _ in ranked[:top_n]]