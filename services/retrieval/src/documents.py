from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


@dataclass
class DocumentChunk:
    id: str
    text: str
    metadata: dict


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> Iterator[str]:
    start = 0
    while start < len(text):
        end = start + chunk_size
        yield text[start:end]
        start += chunk_size - overlap


def load_text_documents(paths: Iterable[Path]) -> Iterator[DocumentChunk]:
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for idx, chunk in enumerate(chunk_text(text)):
            yield DocumentChunk(
                id=f"{path.stem}-{idx}",
                text=chunk,
                metadata={"source": str(path)},
            )
