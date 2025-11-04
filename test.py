from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection
from ollama import chat, ChatResponse
import numpy as np


def ask_faq(query: str,
            collection_name: str = "bob_faqs",
            host: str = "localhost",
            port: str = "19530",
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
    connections.connect("default", host=host, port=port)

    # embed query
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedded_input = model.encode([query]).tolist()

    # search in Milvus
    collection = Collection(collection_name)
    results = collection.search(
        data=embedded_input,
        anns_field="question_embedding",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=2,
        output_fields=["question", "answer"]
    )

    # extract retrieved context
    context_pairs = [
        f"Q: {hit.entity.get('question')}\nA: {hit.entity.get('answer')}"
        for hit in results[0]
    ]
    context_text = "\n\n".join(context_pairs) if context_pairs else "No relevant context found."

    # build system prompt
    system_prompt = (
        "You are a helpful bank assistant.\n"
        f"Given the following context, answer accurately and concisely:\n\n{context_text}\n\n"
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
    answer = ask_faq(question)
    print("\nResponse:", answer)

