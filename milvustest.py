from pymilvus import connections, Collection

connections.connect(alias="default", host="localhost", port="19530")

collection = Collection(name="bob_faqs", using="default", db_name="faqs_db")

# Option A: Query everything (beware large data sets)
result = collection.query(expr='question == "How to contact the Headoffice?"', output_fields=["question", "answer"])
print(result)