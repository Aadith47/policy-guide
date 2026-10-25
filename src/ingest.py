from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

PDF_PATH = Path("../data/handbook.pdf")
MAX_CHARS = 1000
OVERLAP_LINES = 2
SKIP_PAGES = 3  # cover, contents and intro only add noise
FOOTER_PREFIX = "Page |"  # page footer, not policy text


@dataclass
class Chunk:
    id: int
    page: int
    text: str


def read_pages(path):
    pages = []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        # Contents page matches every keyword, so keep it out of the search
        if number <= SKIP_PAGES:
            continue
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((number, text))
    return pages

def clean_line(line):
    # Template values look like [20 days]; keep the value, drop the brackets
    return line.replace("[", "").replace("]", "").strip()


def split_page(text):
    # Clean the brackets first, then throw away empty lines
    cleaned = (clean_line(line) for line in text.splitlines())
    lines = [line for line in cleaned if line]
    chunks = []
    current = []
    size = 0

    for line in lines:
        if size + len(line) > MAX_CHARS and current:
            chunks.append(" ".join(current))
            current = current[-OVERLAP_LINES:]
            size = sum(len(item) + 1 for item in current)
        current.append(line)
        size += len(line) + 1

    if current:
        chunks.append(" ".join(current))
    return chunks


def build_chunks(path=PDF_PATH):
    chunks = []
    for page_number, text in read_pages(path):
        for piece in split_page(text):
            chunks.append(Chunk(id=len(chunks), page=page_number, text=piece))
    return chunks


if __name__ == "__main__":
    chunks = build_chunks()
    print(f"{len(chunks)} chunks")
    for chunk in chunks[:3]:
        print(f"\n[{chunk.id}] page {chunk.page} ({len(chunk.text)} chars)")
        print(chunk.text)