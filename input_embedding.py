from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, MilvusClient
from ollama import chat, ChatResponse
import numpy as np
import sys
import os
from prompt import systemprompt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from databaseHandling import database_handling




def chatrag(query: str,
            bank_name: str,
            search_limit: int = 5,
            embedding_model: str = 'all-MiniLM-L6-v2',
            llm_model: str = "gpt-oss:20b") -> str:
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

    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus",
    )

    client.use_database("Banks_DB")


    # embed query
    model = SentenceTransformer(embedding_model)
    embedded_input = model.encode([query]).tolist()

    results = client.search(
        collection_name=bank_name,
        data=embedded_input,
        anns_field="embedding",
        search_param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=search_limit,
        output_fields=["text", "source"]
    )


    # # search in Milvus
    # collections_list = database_handling.list_collections(client, db_name=database_name)
    # if not collections_list:
    #     return "No collections found in the specified database."
    # results = []
    # for coll in collections_list:
    #     collection = Collection(name=coll, using="default", db_name=database_name)
    #     collection.load()
    #     results.extend(collection.search(
    #         data=embedded_input,
    #         anns_field="question_embedding",
    #         param={"metric_type": "L2", "params": {"nprobe": 10}},
    #         limit=search_limit,
    #         output_fields=["question", "answer"]
    #     ))

    # print(results)
    context = [item["entity"]["text"] for sublist in results for item in sublist]
    context_str = "\n\n".join(context) if context else "No relevant context found."

    # build system prompt
    system_prompt = systemprompt(context_str)

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
    answer = chatrag(question, bank_name="Bank_of_Beirut")
    print("\nResponse:", answer)

