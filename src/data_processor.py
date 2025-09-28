import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
import os
import sys
sys.path.append('..')
from config import KB_DIR, DOCS_DIR, COLLECTION_NAME, EMBEDDING_MODEL

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_txt(txt_path):
    text = ""
    with open(txt_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text

def process_documents(api_key=None):
    """
    Loads documents, chunks them, and stores embeddings in ChromaDB using NVIDIA embeddings.
    """
    # 1. Extract text from all PDFs and TXT files in the docs directory
    full_text = ""
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(DOCS_DIR, filename)
            print(f"Extracting text from {filename}...")
            full_text += extract_text_from_pdf(pdf_path)
        elif filename.endswith(".txt"):
            txt_path = os.path.join(DOCS_DIR, filename)
            print(f"Extracting text from {filename}...")
            full_text += extract_text_from_txt(txt_path)
    
    if not full_text:
        print("No documents found to process!")
        return
    
    # 2. Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ";", ".", " "]
    )
    chunks = text_splitter.split_text(full_text)
    print(f"Created {len(chunks)} chunks.")

    # 3. Create embeddings using NVIDIA and store in ChromaDB
    print(f"Initializing NVIDIA embedding model ({EMBEDDING_MODEL})...")
    
    # Set API key if provided
    if api_key:
        os.environ["NVIDIA_API_KEY"] = api_key
    
    embeddings = NVIDIAEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=api_key or os.getenv("NVIDIA_API_KEY")
    )
    
    print("Creating ChromaDB vector store...")
    db = Chroma.from_texts(
        chunks,
        embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=KB_DIR
    )
    db.persist()
    print("Knowledge base created successfully!")

if __name__ == "__main__":
    if not os.path.exists(DOCS_DIR):
        print(f"Error: Directory '{DOCS_DIR}' not found. Please place your PDFs and text files here.")
    else:
        # Use the provided API key
        api_key = "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"
        process_documents(api_key=api_key)
