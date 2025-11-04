from pymilvus import connections, Collection, MilvusClient
from pymilvus import utility
connections.connect(alias="default", host="localhost", port="19530")

client = MilvusClient(
    uri="http://localhost:19530",
    token="root:Milvus",
)


# List all collections
collections = client.list_collections()

# Print the list of collections
print(collections)

# List all databases
databases = client.list_databases()
print(databases)

collection = Collection(name="Chroma_DB_Filtering", using="default", db_name="default_bank")
collection.load()

# print elements in the collection


result = collection.query(expr='chunk_id>=0', output_fields=["chunk_id", "text"], limit=5)
print(result)