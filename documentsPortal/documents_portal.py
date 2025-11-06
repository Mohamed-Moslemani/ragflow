import os
import re
from PyPDF2 import PdfReader
from pytesseract import image_to_string
from PIL import Image
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pymilvus import FieldSchema, CollectionSchema, DataType, MilvusClient
from sentence_transformers import SentenceTransformer
import logging


def load_document(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    if file_path.endswith(".txt"):
        return load_text_file(file_path)
    if file_path.endswith(".pdf"):
        return load_pdf_file(file_path)
    if file_path.endswith(".jpg") or file_path.endswith(".jpeg") or file_path.endswith(".png"):
        return load_image_file(file_path)
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

def load_image_file(file_path: str) -> str:

    image = Image.open(file_path)
    text = image_to_string(image)
    return text


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
        logging.info("Created and switched to database 'Banks_DB'")


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

    if not client.has_collection(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            schema=schema,
        )
        logging.info(f"Collection '{collection_name}' created.")
    else:
        logging.info(f"Collection '{collection_name}' already exists.")

    if not client.has_partition(collection_name=collection_name, partition_name=partition_name):
        client.create_partition(
            collection_name=collection_name,
            partition_name=partition_name,
        )
        logging.info(f"Partition '{partition_name}' created in collection '{collection_name}'.")
    else:
        client.release_partitions(collection_name=collection_name, partition_names=[partition_name])
        client.drop_partition(collection_name=collection_name, partition_name=partition_name)
        client.create_partition(
            collection_name=collection_name,
            partition_name=partition_name,
        )
        logging.info(f"Partition '{partition_name}' recreated in collection '{collection_name}'.")

    # Prepare data as list of dictionaries matching the schema
    data = []
    for doc in documents:
        data.append({
            "text": doc.page_content,
            "source": doc.metadata["source"],
            "chunk_size": doc.metadata["chunk_size"],
            "chunk_type": doc.metadata["chunk_type"],
            "embedding": doc.metadata["embedding"].tolist(),
        })

    client.insert(
        collection_name=collection_name,
        partition_name=partition_name,
        data=data,
    )

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="embedding",
        index_type="IVF_FLAT",
        metric_type="L2",
        params={"nlist": 128}
    )

    client.create_index(collection_name=collection_name, index_params=index_params)
    client.load_collection(collection_name=collection_name)

    logging.info(f"Inserted {len(documents)} documents into collection '{collection_name}'.")
    
    
def main(file_path: str):
    document_content = load_document(file_path)
    print(document_content)

    # # 2. Chunk into Document objects with metadata
    # chunked_docs = perform_semantic_chunking(
    #     document=document_content,
    #     source=file_path,
    #     chunk_size=500,
    #     chunk_overlap=100,
    # )
    # print(chunked_docs)

    # # 3. Embed chunks
    # embedded_docs = perform_embedding_generation(
    #     chunked_docs=chunked_docs,
    #     model_name='all-MiniLM-L6-v2',
    # )
    # # 4. Store in database
    # toDB(embedded_docs, collection_name="testChunk", partition_name="faqs_db")

if __name__ == "__main__":
    test_file_path = "image_2.png"  
    main(test_file_path)
