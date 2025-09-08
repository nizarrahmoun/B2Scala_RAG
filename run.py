"""
Quick run script for B2Scala-RAG-NVIDIA
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔹 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(e.stderr)
        return False

def main():
    """Main run function."""
    if len(sys.argv) < 2:
        print("🚀 B2Scala-RAG-NVIDIA Quick Run")
        print("===============================")
        print("Usage: python run.py <command>")
        print("\nAvailable commands:")
        print("  install    - Install dependencies")
        print("  train      - Train the knowledge base")
        print("  app        - Run Streamlit app")
        print("  pipeline   - Run RAG pipeline")
        print("  test       - Test the system")
        print("  all        - Run complete setup")
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        run_command("pip install -r requirements.txt", "Installing dependencies")
    
    elif command == "train":
        run_command("cd src && python data_processor.py", "Training knowledge base")
    
    elif command == "app":
        run_command("streamlit run app.py", "Starting Streamlit app")
    
    elif command == "pipeline":
        run_command("cd src && python rag_pipeline.py", "Running RAG pipeline")
    
    elif command == "test":
        run_command("python train.py test", "Testing the system")
    
    elif command == "all":
        print("🚀 Running complete setup...")
        
        steps = [
            ("pip install -r requirements.txt", "Installing dependencies"),
            ("cd src && python data_processor.py", "Training knowledge base"),
            ("python train.py test", "Testing the system")
        ]
        
        for cmd, desc in steps:
            if not run_command(cmd, desc):
                print("❌ Setup failed!")
                return
        
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python run.py app' to start the web interface")
        print("2. Run 'python run.py pipeline' to test the RAG pipeline")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python run.py' to see available commands.")

if __name__ == "__main__":
    main()
