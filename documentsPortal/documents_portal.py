import os
import re
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def load_document(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    if file_path.endswith(".txt"):
        return load_text_file(file_path)
    if file_path.endswith(".pdf"):
        return load_pdf_file(file_path)

    raise ValueError(f"Unsupported file type for {file_path}")


def load_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def load_pdf_file(file_path: str) -> str:
    reader = PdfReader(file_path)
    content = ""
    for page in reader.pages:
        text = page.extract_text() or ""
        content += text + "\n"
    return content


def perform_semantic_chunking(
    document: str,
    source: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
):

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", "", "? "],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    semantic_chunks = text_splitter.split_text(document)
    print(f"Document split into {len(semantic_chunks)} semantic chunks")

    section_patterns = [
        r"^#+\s+(.+)$",      # Markdown headers:  ## Section
        r"^.+\n[=\-]{2,}$",  # Underlined headers
        r"^[A-Z\s]+:$",      # ALL CAPS section titles:
    ]

    documents = []

    for i, chunk in enumerate(semantic_chunks):
        chunk_lines = chunk.split("\n")
        for line in chunk_lines:
            for pattern in section_patterns:
                if re.match(pattern, line.strip()):
                    chunk_type = "section_header"
                    break
                else:
                    chunk_type = "semantic"
            
        words = re.findall(r"\b\w+\b", chunk.lower())

        doc = Document(
            page_content=chunk,
            metadata={
                "source": source,
                "chunk_id": i,
                "total_chunks": len(semantic_chunks),
                "chunk_size": len(chunk),
                "chunk_type": "semantic",
            },
        )
        documents.append(doc)

    return documents


def main(file_path: str):
    # 1. Load raw content
    document_content = load_document(file_path)

    # 2. Chunk into Document objects with metadata
    chunked_docs = perform_semantic_chunking(
        document=document_content,
        source=file_path,
        chunk_size=500,
        chunk_overlap=100,
    )

    print("\n----- CHUNKING RESULTS -----")
    print(f"Total semantic chunks: {len(chunked_docs)}")

    # Show an example chunk
    # middle_chunk_idx = len(chunked_docs) // 2 if chunked_docs else 0
    middle_chunk_idx = 0
    if chunked_docs:
        example_chunk = chunked_docs[middle_chunk_idx]
        print("\n----- EXAMPLE SEMANTIC CHUNK -----")
        print(f"Chunk {middle_chunk_idx} content ({len(example_chunk.page_content)} characters):")
        print("-" * 40)
        print(example_chunk.page_content[:1000])  # don’t print 10k chars
        print("-" * 40)
        print(f"Metadata: {example_chunk.metadata}")


if __name__ == "__main__":
    test_file_path = "Chroma_DB_Filtering.pdf"  # Change to your test file path
    main(test_file_path)
