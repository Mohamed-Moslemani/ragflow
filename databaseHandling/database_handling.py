from pymilvus import connections, Collection, MilvusClient, utility, CollectionSchema, FieldSchema, DataType

try:
    connections.disconnect(alias="default")
    connections.connect(alias="default", host="localhost", port="19530")
except:
    connections.connect(alias="default", host="localhost", port="19530")


def list_collections(client, db_name: str):
    return client.list_collections(db_name=db_name)

def create_collection(collection_name: str, schema: CollectionSchema, db_name: str, **kwargs):
    if utility.has_collection(collection_name=collection_name, using="default"):
        print(f"Collection '{collection_name}' already exists.")
        return Collection(name=collection_name, using="default", db_name=db_name)
    else:
        collection = Collection(
            name=collection_name,
            schema=schema,
            using="default",
            db_name=db_name,
            **kwargs
        )
        print(f"Collection '{collection_name}' created.")
        return collection
    
def delete_collection(client, collection_name: str, db_name: str):
    collections = client.list_collections(db_name=db_name)
    if collection_name in collections:
        client.drop_collection(collection_name, db_name=db_name)
        print(f"Collection '{collection_name}' deleted from database '{db_name}'.")
    else:
        print(f"Collection '{collection_name}' does not exist in database '{db_name}'.")


def delete_database(client, db_name: str):
    try:
        collections = client.list_collections(db_name=db_name)
        for coll in collections:
            delete_collection(client, collection_name=coll, db_name=db_name)
        client.drop_database(db_name=db_name)
        print(f"Database '{db_name}' dropped.")
    except Exception as e:
        print(f"Failed to drop database '{db_name}': {e}")


def create_database(client, db_name: str):
    try:
        client.create_database(db_name=db_name)
        print(f"Database '{db_name}' created.")
    except Exception as e:
        print(f"Database creation skipped: {e}")


def main():
    db_name = "default_bank"

    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus",
    )

    create_database(client, db_name)

    create_collection(
        collection_name="testChunks",
        schema=CollectionSchema(
            fields=[
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=2048),
                FieldSchema(name="question_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name="answer_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
            ],
            description="FAQ embeddings (question + answer)"
        ),
        db_name=db_name,
        shards_num=2,
    )

    list_collections(client, "faqs_db")

    delete_collection(client, "testChunks", db_name)

    create_collection(
        collection_name="testChunks",
        schema=CollectionSchema(
            fields=[
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=2048),
                FieldSchema(name="question_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name="answer_embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
            ],
            description="FAQ embeddings (question + answer)"
        ),
        db_name=db_name,
        shards_num=2,
    )

    delete_database(client, db_name)


if __name__ == "__main__":
    main()
