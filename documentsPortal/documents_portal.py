import os
import re
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility, MilvusClient
from sentence_transformers import SentenceTransformer
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from databaseHandling import database_handling


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

def perform_embedding_generation(chunked_docs: list, model_name: str) -> list:
    model = SentenceTransformer(model_name)
    texts = [doc.page_content for doc in chunked_docs]
    embeddings = model.encode(texts, convert_to_numpy=True).astype("float32")
    for doc, embedding in zip(chunked_docs, embeddings):
        doc.metadata["embedding"] = embedding
        
    return chunked_docs

def toDB(documents, partition_name="document_chunks", collection_name="default_bank"):

    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus",
    )
    try:
        client.use_database("Banks_DB")
    except:
        client.create_database("Banks_DB")
        client.use_database("Banks_DB")


    schema = CollectionSchema(
        [
            FieldSchema(name="chunk_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="chunk_size", dtype=DataType.INT64),
            FieldSchema(name="chunk_type", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=len(documents[0].metadata["embedding"])),
        ],
        description="Document chunks with embeddings",
    )
    try:
        collection = Collection(name=collection_name, schema=schema)
        print(f"Collection '{collection_name}' already exists.")
        logging.info(f"Collection '{collection_name}' already exists.")
    except:
        client.create_collection(
            collection_name=collection_name,
            schema=schema,
        )
        print(f"Collection '{collection_name}' created.")
        collection = Collection(name=collection_name, schema=schema)
        logging.info(f"Collection '{collection_name}' created.")

    try:
        logging.info(f"Dropping existing partition '{partition_name}' and recreating it with updated chunks.")
        collection.drop_partition(partition_name=partition_name)
        collection.create_partition(partition_name=partition_name)
    except:
        collection.create_partition(partition_name=partition_name)
        logging.info(f"Partition '{partition_name}' created.")

    chunk_ids = [doc.metadata["chunk_id"] for doc in documents]
    texts = [doc.page_content for doc in documents]
    sources = [doc.metadata["source"] for doc in documents]
    chunk_sizes = [doc.metadata["chunk_size"] for doc in documents]
    chunk_types = [doc.metadata["chunk_type"] for doc in documents]
    embeddings = [doc.metadata["embedding"] for doc in documents]

    client.insert(
        collection_name=collection_name,
        partition_name=partition_name,
        data=[
            texts,
            sources,
            chunk_sizes,
            chunk_types,
            embeddings,
        ],
    )

    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128},
    }

    client.create_index(collection_name=collection_name, field_name="embedding", index_params=index_params)
    client.load_collection(collection_name=collection_name)

    logging.info(f"Inserted {len(documents)} documents into collection '{collection_name}'.")
    
    
def main(file_path: str):
    document_content = load_document(file_path)

    # 2. Chunk into Document objects with metadata
    chunked_docs = perform_semantic_chunking(
        document=document_content,
        source=file_path,
        chunk_size=500,
        chunk_overlap=100,
    )
    print(chunked_docs)

    # 3. Embed chunks
    embedded_docs = perform_embedding_generation(
        chunked_docs=chunked_docs,
        model_name='all-MiniLM-L6-v2',
    )
    # 4. Store in database
    toDB(embedded_docs, collection_name="testChunk", partition_name="faqs_db")

if __name__ == "__main__":
    test_file_path = "Chroma_DB_Filtering.pdf"  
    main(test_file_path)
