"""
Training Script for B2Scala-RAG-NVIDIA
This script demonstrates how to train/fine-tune the system using additional examples.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_processor import process_documents
from src.rag_pipeline import RAGPipeline
from src.retriever import Retriever
from config import NVIDIA_API_KEY, DOCS_DIR

def train_knowledge_base():
    """
    Process all documents in the docs directory to create/update the knowledge base.
    This is the main 'training' step for the RAG system.
    """
    print("🔹 Starting knowledge base training...")
    
    # Check if docs directory exists and has files
    if not os.path.exists(DOCS_DIR):
        print(f"❌ Error: '{DOCS_DIR}' directory not found!")
        return False
    
    files = [f for f in os.listdir(DOCS_DIR) if f.endswith(('.pdf', '.txt', '.scala'))]
    if not files:
        print("❌ Error: No training files found in 'docs' directory!")
        return False
    
    print(f"📚 Found {len(files)} training files:")
    for file in files:
        print(f"   - {file}")
    
    try:
        # Process documents and create embeddings
        process_documents(api_key=NVIDIA_API_KEY)
        print("✅ Knowledge base training completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False

def test_trained_model():
    """
    Test the trained model with example queries.
    """
    print("\n🔹 Testing trained model...")
    
    try:
        # Initialize RAG pipeline
        rag = RAGPipeline(k=5, api_key=NVIDIA_API_KEY)
        
        # Test queries
        test_queries = [
            "Simple authentication protocol with client and server",
            "Key exchange using Diffie-Hellman",
            "TLS handshake protocol",
            "Kerberos authentication"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test Query {i}: {query}")
            
            try:
                # Get context
                retriever = Retriever(k=3, api_key=NVIDIA_API_KEY)
                context = retriever.get_context(query)
                
                print(f"   Retrieved {len(context)} relevant examples")
                
                # Generate code (optional - can be time consuming)
                # answer, _ = rag.generate_answer(query)
                # print(f"   Generated code length: {len(answer) if answer else 0} characters")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("✅ Model testing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def add_training_example(title, content, file_type="txt"):
    """
    Add a new training example to the knowledge base.
    
    Args:
        title (str): Name of the example
        content (str): Content of the example
        file_type (str): File extension (txt, scala, etc.)
    """
    filename = f"{title.replace(' ', '_').lower()}.{file_type}"
    filepath = os.path.join(DOCS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Added training example: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error adding example: {e}")
        return False

def interactive_training():
    """
    Interactive training mode where users can add examples.
    """
    print("\n🎯 Interactive Training Mode")
    print("Add new B2Scala examples to improve the model.")
    
    while True:
        print("\nOptions:")
        print("1. Add new example")
        print("2. Retrain knowledge base")
        print("3. Test model")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            title = input("Enter example title: ").strip()
            if not title:
                print("❌ Title cannot be empty!")
                continue
            
            print("Enter example content (end with '###' on a new line):")
            content_lines = []
            while True:
                line = input()
                if line.strip() == "###":
                    break
                content_lines.append(line)
            
            content = "\n".join(content_lines)
            if content.strip():
                add_training_example(title, content)
            else:
                print("❌ Content cannot be empty!")
        
        elif choice == "2":
            train_knowledge_base()
        
        elif choice == "3":
            test_trained_model()
        
        elif choice == "4":
            print("👋 Exiting interactive training mode.")
            break
        
        else:
            print("❌ Invalid choice! Please enter 1-4.")

def main():
    """
    Main training function.
    """
    print("🚀 B2Scala-RAG-NVIDIA Training Script")
    print("=====================================")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "train":
            train_knowledge_base()
        elif mode == "test":
            test_trained_model()
        elif mode == "interactive":
            interactive_training()
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: train, test, interactive")
    
    else:
        # Default: run full training pipeline
        print("🔹 Running full training pipeline...")
        
        # Step 1: Train knowledge base
        if train_knowledge_base():
            # Step 2: Test the trained model
            test_trained_model()
        
        print("\n✅ Training pipeline completed!")
        print("\nNext steps:")
        print("1. Run 'streamlit run app.py' to start the web interface")
        print("2. Run 'python train.py interactive' for interactive training")
        print("3. Add more examples to 'docs/' directory and retrain")

if __name__ == "__main__":
    main()
