# backend/core/parser.py
def break_into_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split('\n') if p.strip()]
