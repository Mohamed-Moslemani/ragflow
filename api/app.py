from fastapi import FastAPI, UploadFile, File, Form
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documentsPortal import documents_portal
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = "uploaded_files/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

selected_bank_name = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Processing API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/bankname")
async def add_bank_name(bank_name: str = Form(...)):
    global selected_bank_name
    selected_bank_name = bank_name
    return {"bank_name": bank_name, "message": "Bank name received successfully."}

@app.post("/documents")
async def add_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": file.filename, "message": "File uploaded successfully."}

@app.get("/documents/{filename}/process")
async def process_document(filename: str):
    global selected_bank_name
    if selected_bank_name is None:
        return {"error": "Bank name not set. Please set the bank name before processing documents."}
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": f"File '{filename}' not found."}
    filename = os.path.basename(filename)
    filename, _ = os.path.splitext(filename)
    document = documents_portal.load_document(file_path)
    chunks = documents_portal.perform_semantic_chunking(
        document=document,
        source=file_path,
    )
    chunks = documents_portal.perform_embedding_generation(
        chunked_docs=chunks,
        model_name="all-MiniLM-L6-v2",
    )
    documents_portal.toDB(
        documents=chunks,
        collection_name=filename,
        bank_name=selected_bank_name,
    )
    return {"message": f"Document '{filename}' processed and stored in database."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)