SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separators: list[str] | None = None,
) -> list[str]:
    """Recursive character text splitter."""
    if separators is None:
        separators = SEPARATORS
    return _split_recursive(text, chunk_size, chunk_overlap, separators, 0)


def _split_recursive(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: list[str],
    sep_index: int,
) -> list[str]:
    if len(text) <= chunk_size:
        stripped = text.strip()
        return [stripped] if stripped else []

    sep = separators[sep_index] if sep_index < len(separators) else ""
    next_sep = min(sep_index + 1, len(separators) - 1)

    if sep == "":
        # Last resort: hard split by chunk_size
        chunks = []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk = text[i : i + chunk_size].strip()
            if chunk:
                chunks.append(chunk)
        return chunks

    parts = text.split(sep)
    chunks = []
    current = ""

    for part in parts:
        candidate = current + sep + part if current else part

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                stripped = current.strip()
                if stripped:
                    chunks.append(stripped)

            if len(part) > chunk_size:
                # Recursively split with next separator
                sub_chunks = _split_recursive(
                    part, chunk_size, chunk_overlap, separators, next_sep
                )
                chunks.extend(sub_chunks)
                current = ""
            else:
                # Start overlap from end of previous chunk
                if chunks and chunk_overlap > 0:
                    overlap_text = chunks[-1][-chunk_overlap:]
                    current = overlap_text + sep + part
                    if len(current) > chunk_size:
                        current = part
                else:
                    current = part

    if current and current.strip():
        chunks.append(current.strip())

    return chunks
