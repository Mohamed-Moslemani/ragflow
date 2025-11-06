from pymilvus import connections, Collection, MilvusClient, FieldSchema, CollectionSchema, DataType
import os
import sys


def reset_all_database():
    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus",
    )

    # Delete existing database
    databases = client.list_databases()
    for db in databases:
        client.use_database(db_name=db)
        collections = client.list_collections(db_name=db)
        for coll in collections:
            client.drop_collection(collection_name=coll)
        if db != "default":
            client.drop_database(db_name=db)
        print(f"Dropped database '{db}'.")

if __name__ == "__main__":
    reset_all_database()