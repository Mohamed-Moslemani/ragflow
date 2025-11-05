from pymilvus import connections, Collection, MilvusClient, FieldSchema, CollectionSchema, DataType
import os
import sys
import databaseHandling.database_handling as db_handling


def reset_all_database():
    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus",
    )

    # Delete existing database
    databases = client.list_databases()
    for db in databases:
        db_handling.delete_database(client, db_name=db)

if __name__ == "__main__":
    reset_all_database()