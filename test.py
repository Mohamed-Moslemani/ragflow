from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, MilvusClient
from ollama import chat, ChatResponse
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from databaseHandling import database_handling




def chatrag(query: str,
            database_name: str,
            search_limit: int = 5,
            embedding_model: str = 'all-MiniLM-L6-v2',
            llm_model: str = "gpt-oss:latest") -> str:
    """
    Perform semantic search over Milvus FAQ collection and generate an LLM-based answer.

    Args:
        query (str): The user's input question.
        collection_name (str): Milvus collection name. Defaults to "bob_faqs".
        host (str): Milvus host address. Defaults to localhost.
        port (str): Milvus port. Defaults to 19530.
        llm_model (str): LLM model name for Ollama chat. Defaults to gpt-oss:latest.

    Returns:
        str: The generated LLM response.
    """

    # connect to Milvus
    try:
        connections.disconnect(alias=database_name)
        connections.connect(database_name, host="localhost", port="19530")
    except:
        connections.connect(database_name, host="localhost", port="19530")

    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus",
        db_name=database_name,
    )

    # embed query
    model = SentenceTransformer(embedding_model)
    embedded_input = model.encode([query]).tolist()

    # search in Milvus
    collections_list = database_handling.list_collections(client, db_name=database_name)
    if not collections_list:
        return "No collections found in the specified database."
    results = []
    for coll in collections_list:
        collection = Collection(name=coll, using="default", db_name=database_name)
        collection.load()
        results.extend(collection.search(
            data=embedded_input,
            anns_field="question_embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},
            limit=search_limit,
            output_fields=["question", "answer"]
        ))

    # sort results by distance
    results.sort(key=lambda x: x[0].distance)
    results = results[0][:search_limit]

    context = [hit.entity for hit in results]
    context_str = "\n\n".join(context) if context else "No relevant context found."

    # build system prompt
    system_prompt = (
        "You are a helpful bank assistant.\n"
        f"Given the following context, answer accurately and concisely:\n\n{context_str}\n\n"
        "If no context is available, reply: \"I didn't find any available info on this.\""
    )

    # chat with LLM
    response: ChatResponse = chat(
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    return response["message"]["content"]


# Example usage:
if __name__ == "__main__":
    question = input("What is your query? ")
    answer = (question)
    print("\nResponse:", answer)

