from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# 1. connect to Milvus
connections.connect(alias="default", host="localhost", port="19530")

# 2. create database if not exists
try:
    utility.create_database("faqs_db")
except Exception as e:
    print(f"Database creation skipped: {e}")

# 3. load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# 4. define schema with two vector fields
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=2048),
    FieldSchema(name="question_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
    FieldSchema(name="answer_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
]
schema = CollectionSchema(fields, description="FAQ embeddings (question + answer)")

# 5. recreate collection
collection_name = "bob_faqs"
if utility.has_collection(collection_name=collection_name, using="default"):
    utility.drop_collection(collection_name=collection_name, using="default")

collection = Collection(
    name=collection_name,
    schema=schema,
    using="default",
    db_name="faqs_db",
    shards_num=2,
)

# 6. load data
json_file = 'bank_of_beirut_faq_organized.json'
with open(json_file, 'r', encoding='utf-8') as f:
    faq_data = json.load(f)

questions, answers = [], []
for category, qas in faq_data.items():
    for qa in qas:
        questions.append(qa['question'])
        answers.append(qa['answer'])

# 7. generate embeddings for both fields
question_embeddings = model.encode(questions, convert_to_numpy=True).astype("float32")
answer_embeddings = model.encode(answers, convert_to_numpy=True).astype("float32")

# 8. insert data (order must match schema excluding auto_id)
entities = [
    questions,
    answers,
    question_embeddings,
    answer_embeddings,
]
collection.insert(entities)

# 9. create indexes for both embedding fields
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
}

collection.create_index(field_name="question_embedding", index_params=index_params)
collection.create_index(field_name="answer_embedding", index_params=index_params)

# 10. load for search
collection.load()

print("Inserted and indexed 'bob_faqs' with separate question + answer embeddings.")
