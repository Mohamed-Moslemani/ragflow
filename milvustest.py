from pymilvus import connections, Collection, MilvusClient
from pymilvus import utility
import sys
import os

connections.connect(alias="default", host="localhost", port="19530")

client = MilvusClient(
    uri="http://localhost:19530",
    token="root:Milvus",
    db_name="default",
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from databaseHandling import database_handling

# List all collections
collections = client.list_collections()

# Print the list of collections
print(collections)

# List all databases
databases = client.list_databases()
print(databases)

# delete_db_name = "BankMed"
# database_handling.delete_database(client, db_name=delete_db_name)

# collection = Collection(name="Chroma_DB_Filtering", using="default", db_name="default_bank")
# collection.load()

# print elements in the collection


# result = collection.query(expr='chunk_id>=0', output_fields=["chunk_id", "text"], limit=5)
# print(result)