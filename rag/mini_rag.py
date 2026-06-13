import re


def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 180) -> list[str]:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return []

    chunks = []
    start = 0

    while start < len(cleaned):
        end = start + chunk_size
        chunk = cleaned[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(cleaned):
            break

        start = max(0, end - overlap)

    return chunks


def search_relevant_chunks(query: str, chunks: list[dict[str, str]], limit: int = 4) -> list[dict[str, str]]:
    query_terms = _tokenize(query)
    scored_chunks = []

    for chunk in chunks:
        chunk_text = chunk.get("chunk_text", "")
        file_name = chunk.get("file_name", "")
        chunk_terms = _tokenize(chunk_text)
        file_terms = _tokenize(file_name)
        score = len(query_terms.intersection(chunk_terms))
        score += len(query_terms.intersection(file_terms)) * 2

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored_chunks[:limit]]


def format_context(chunks: list[dict[str, str]]) -> str:
    if not chunks:
        return ""

    lines = []
    for chunk in chunks:
        source = chunk.get("file_name", "uploaded document")
        text = chunk.get("chunk_text", "")
        lines.append(f"Source: {source}\n{text}")

    return "\n\n".join(lines)


def _tokenize(text: str) -> set[str]:
    tokens = {
        token
        for token in re.findall(r"[\wа-яА-ЯёЁ]+", (text or "").lower())
        if len(token) > 2
    }

    expanded_tokens = set(tokens)
    for token in tokens:
        if len(token) > 5:
            expanded_tokens.add(token[:5])
        expanded_tokens.update(_synonyms(token))

    return expanded_tokens


def _synonyms(token: str) -> set[str]:
    synonyms = {
        "смартфон": {"smartphone", "phone"},
        "смартфона": {"smartphone", "phone"},
        "смартфоны": {"smartphone", "phone"},
        "ноутбук": {"laptop"},
        "ноутбука": {"laptop"},
        "ноутбуки": {"laptop"},
        "доставки": {"доставка", "достав"},
        "доставку": {"доставка", "достав"},
        "возврата": {"возврат", "вернуть"},
        "вернуть": {"возврат"},
        "отменить": {"отмена"},
    }
    return synonyms.get(token, set())
