"""Split markdown documents into chunks by heading, keeping metadata for provenance."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from assistant_core.errors import DataError


@dataclass(frozen=True)
class Chunk:
    id: str  # e.g. "H26#5.3"
    doc_id: str
    title: str  # section heading
    text: str
    version: str
    owner: str


def _front_matter(raw: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n", raw, flags=re.S)
    if not m:
        return {}, raw
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    return {k.strip(): v.strip() for k, v in meta.items()}, raw[m.end() :]


def chunk_markdown(path: Path) -> list[Chunk]:
    meta, body = _front_matter(path.read_text(encoding="utf-8"))
    doc_id = meta.get("doc_id", path.stem)
    chunks = []
    for part in re.split(r"^#[ \t]+(?=\S)", body, flags=re.M)[1:]:
        heading, _, text = part.partition("\n")
        number = heading.split()[0]
        chunks.append(
            Chunk(
                id=f"{doc_id}#{number}",
                doc_id=doc_id,
                title=heading.strip(),
                text=" ".join(text.split()),
                version=meta.get("version", "?"),
                owner=meta.get("owner", "?"),
            )
        )
    return chunks


def load_folder(folder: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    seen: set[str] = set()
    for path in sorted(folder.glob("*.md")):
        for chunk in chunk_markdown(path):
            if chunk.id in seen:
                raise DataError(f"Duplicate chunk ID {chunk.id} in {path.name}")
            chunks.append(chunk)
            seen.add(chunk.id)
    return chunks
