from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection
import numpy as np
from ollama import chat,ChatResponse
# connect
connections.connect("default", host="localhost", port="19530")
# model
model = SentenceTransformer('all-MiniLM-L6-v2')

# embed query
input_usr = input("What is your query? ")
embedded_input = model.encode([input_usr]).tolist()

# collection
collection = Collection("bob_faqs")

# search
res = collection.search(
    data=embedded_input,
    anns_field="question_embedding",
    param={"metric_type": "L2", "params": {"nprobe": 10}},
    limit=2,
    output_fields=["question", "answer"]
)

response: ChatResponse= chat(model="gpt-oss:latest",
                             messages= [
                                 {
                                     "role": 'user',
                                     "content": input_usr,
                                     "context": res
                            
                                 }
                             ])

print(response["message"]["content"])