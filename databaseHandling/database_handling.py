from pymilvus import connections, Collection, MilvusClient, utility, CollectionSchema, FieldSchema, DataType

try:
    connections.disconnect(alias="default")
    connections.connect(alias="default", host="localhost", port="19530")
except:
    connections.connect(alias="default", host="localhost", port="19530")

client = MilvusClient(
    uri="http://localhost:19530",
    token="root:Milvus"
)

def list_collections():
    collections = client.list_collections()
    return collections

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

def delete_collection(collection_name: str):
    if utility.has_collection(collection_name=collection_name, using="default"):
        utility.drop_collection(collection_name=collection_name, using="default")
        print(f"Collection '{collection_name}' deleted.")
    else:
        print(f"Collection '{collection_name}' does not exist.")

def create_database(db_name: str):
    try:
        utility.create_database(db_name)
        print(f"Database '{db_name}' created.")
    except Exception as e:
        print(f"Database creation skipped: {e}")
    
def delete_database(db_name: str):
    try:
        collections = list_collections()
        for coll in collections:
            delete_collection(collection_name=coll)
        client.drop_database(db_name)
        print(f"Database '{db_name}' dropped.")
    except Exception as e:
        print(f"Failed to drop database '{db_name}': {e}")


def main():
    collections = list_collections()
    print("Collections in the database:")
    for coll in collections:
        print(f"- {coll}")

if __name__ == "__main__":
    create_database("faqs_db")
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
        db_name="faqs_db",
        shards_num=2,
    )
    main()
    delete_database("faqs_db")
    main()
