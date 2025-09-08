from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.vectorstores import Chroma
import os
import sys
sys.path.append('..')
from config import KB_DIR, COLLECTION_NAME, EMBEDDING_MODEL

class Retriever:
    def __init__(self, k=5, api_key=None):
        print("🔹 Initializing NVIDIA embeddings...")
        
        # Use provided API key or get from environment
        if api_key:
            os.environ["NVIDIA_API_KEY"] = api_key
        
        embeddings = NVIDIAEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=api_key or os.getenv("NVIDIA_API_KEY")
        )

        print("🔹 Loading ChromaDB knowledge base...")
        self.db = Chroma(
            persist_directory=KB_DIR,
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME
        )
        self.k = k

    def get_context(self, query):
        print(f"🔹 Retrieving top {self.k} documents...")
        retrieved_docs = self.db.similarity_search(query, k=self.k)
        return [doc.page_content for doc in retrieved_docs]

if __name__ == "__main__":
    # For testing purposes
    api_key = "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"
    retriever = Retriever(k=3, api_key=api_key)
    query = "Define an agent named Alice that uses the primitives tell and get."
    context = retriever.get_context(query)
    print("\n--- Retrieved Context ---")
    for c in context:
        print(c)
        print("---")
