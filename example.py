"""
Example usage of the B2Scala-RAG-NVIDIA system
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_pipeline import RAGPipeline
from config import NVIDIA_API_KEY, GENERATED_DIR

# Example protocol draft
EXAMPLE_DRAFT = """
Title: Simplified TLS Handshake
Agents:
  - Client
  - Server
Messages:
  - Client -> Server: ClientHello(randomC, cipherSuites)
  - Server -> Client: ServerHello(randomS, cipherSuite, certificate)
  - Client -> Server: ClientKeyExchange(premaster_secret_encrypted)
  - Server -> Client: ChangeCipherSpec()
  - Server -> Client: Finished(MAC)
  - Client -> Server: ChangeCipherSpec()
  - Client -> Server: Finished(MAC)
Goals:
  - Server authentication
  - Key establishment
  - Secure communication channel
Assumptions:
  - Server has valid certificate
  - Client trusts CA
  - RSA key exchange
  - Symmetric encryption for data
"""

def run_example():
    """Run an example of the B2Scala code generation."""
    print("🚀 B2Scala-RAG-NVIDIA Example")
    print("==============================")
    
    # Initialize the RAG pipeline
    print("🔹 Initializing RAG pipeline...")
    rag = RAGPipeline(k=5, api_key=NVIDIA_API_KEY)
    
    print("📝 Protocol Draft:")
    print(EXAMPLE_DRAFT)
    print("\n" + "="*50)
    
    # Generate B2Scala code
    print("🔹 Generating B2Scala code...")
    answer, context = rag.generate_answer(EXAMPLE_DRAFT)
    
    if answer:
        print("✅ Code generation successful!")
        
        # Save the generated code
        os.makedirs(GENERATED_DIR, exist_ok=True)
        output_file = os.path.join(GENERATED_DIR, "example_tls_handshake.scala")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(answer)
        
        print(f"💾 Generated code saved to: {output_file}")
        
        # Show the first few lines
        lines = answer.split('\n')
        print("\n📄 Generated Code (preview):")
        print("="*50)
        for line in lines[:20]:  # Show first 20 lines
            print(line)
        
        if len(lines) > 20:
            print("... (truncated)")
        
        print("="*50)
        print(f"📊 Total lines generated: {len(lines)}")
        
        # Show retrieved context
        print(f"\n📚 Retrieved {len(context)} relevant examples from knowledge base")
        
    else:
        print("❌ Code generation failed!")

if __name__ == "__main__":
    run_example()
