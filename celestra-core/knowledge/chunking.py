"""Text chunking utilities for RAG ingestion."""

from __future__ import annotations


def chunk_text(text: str, *, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """
    Split text into overlapping character windows.

    Foundation splitter — swap for token-aware chunkers later without changing callers.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    chunks: list[str] = []
    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + chunk_size, length)
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        start = end - overlap
    return chunks
