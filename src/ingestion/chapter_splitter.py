import re
from src.utils import clean_text

def split_into_chapters(full_text: str) -> list:
    """
    Tries to detect chapters by headings such as:
    Chapter 1, CHAPTER 2, Lesson 3, Unit 4, etc.
    Falls back to one big chapter if nothing is found.
    """
    pattern = re.compile(
        r"(?im)^(chapter\s+\d+.*|lesson\s+\d+.*|unit\s+\d+.*|chapter\s+[ivxlcdm]+.*)$"
    )

    matches = list(pattern.finditer(full_text))
    chapters = []

    if not matches:
        return [{
            "chapter_id": 1,
            "chapter_title": "Full Book",
            "text": clean_text(full_text)
        }]

    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(full_text)

        title = clean_text(match.group(0))
        body = clean_text(full_text[start:end])

        chapters.append({
            "chapter_id": idx + 1,
            "chapter_title": title,
            "text": body
        })

    return chapters