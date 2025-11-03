from pymilvus import MilvusClient, connections, FieldSchema, CollectionSchema, DataType, Collection, db, model
from sentence_transformers import SentenceTransformer
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

try:
    connections.connect(alias="default", host="localhost", port="19530")
except Exception as e:
    print(f"Connection to Milvus failed: {e}")

try:
    db.create_database("faqs_db")
except Exception as e:
    print(f"Database creation skipped: {e}")


client = MilvusClient(db_name="faqs_db")
if client.has_collection(collection_name="bob_faqs"):
    client.drop_collection(collection_name="bob_faqs")
client.create_collection(
    collection_name="bob_faqs",
    dimension=384,
)
collection = client.get_collection("bob_faqs")

json_file = 'data/Bank_of_Beirut/bank_of_beirut_faq_organized.json'
with open(json_file, 'r', encoding='utf-8') as f:
    faq_data = json.load(f)
questions = []
answers = []
for category, qas in faq_data.items():
    for qa in qas:
        questions.append(qa['question'])
        answers.append(qa['answer'])
embeddings = model.encode(questions)
entities = {
    "embeddings": embeddings,
    "question": questions,
    "answer": answers
}
collection.insert(entities)
collection.create_index(field_name="embeddings", index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}})
collection.load()
print("Data inserted and indexed successfully in Milvus collection 'bob_faqs'.")


