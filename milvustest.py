from pymilvus import connections, Collection, MilvusClient
from pymilvus import utility
connections.connect(alias="default", host="localhost", port="19530")

client = MilvusClient(
    uri="http://localhost:19530",
    token="root:Milvus"
)


# List all collections
collections = client.list_collections()

# Print the list of collections
print(collections)

# List all databases
databases = client.list_databases()
print(databases)

# collection = Collection(name="testChunk", using="default", db_name="faqs_db")
# collection.load()

# result = collection.query(expr='chunk_id==461962138324829013', output_fields=["chunk_id", "text"], limit=5)
# print(result)