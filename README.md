# B2Scala-RAG-NVIDIA 🚀

A powerful **Retrieval-Augmented Generation (RAG)** system that automatically generates **B2Scala** protocol implementations from natural language descriptions, protocol drafts, PDF documents, images, and existing Scala code. Powered by **NVIDIA AI Endpoints** and **DeepSeek v3.1**.

![B2Scala-RAG-NVIDIA](https://img.shields.io/badge/B2Scala-RAG--NVIDIA-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-red)
![Python](https://img.shields.io/badge/Python-3.13-green)
![NVIDIA](https://img.shields.io/badge/NVIDIA-AI%20Endpoints-brightgreen)

## 🎯 Overview

This project bridges the gap between **protocol specifications** and **formal verification** by automatically converting natural language protocol descriptions into executable **B2Scala** code. The system uses a sophisticated RAG pipeline with NVIDIA's embedding models and DeepSeek's language model to generate syntactically correct and semantically meaningful B2Scala implementations.

## ✨ Key Features

### 🧠 AI-Powered Code Generation
- **NVIDIA AI Endpoints** integration with DeepSeek v3.1
- **RAG-based context retrieval** from B2Scala knowledge base
- **Streaming responses** with reasoning visualization
- **Template-based generation** ensuring consistent code structure

### 📁 Multi-Format Input Support
- **📝 Text Input**: Natural language protocol descriptions
- **📄 PDF Upload**: Extract text from protocol specification documents
- **🖼️ Image Upload**: OCR-powered text extraction from diagrams and handwritten notes
- **⚙️ Scala Upload**: Process existing B2Scala implementations for modification
- **🔄 Combined Input**: Mix uploaded content with additional instructions

### 🎨 Interactive Web Interface
- **Streamlit-based UI** with real-time code generation
- **Syntax highlighting** for generated Scala code
- **File type icons** and smart previews
- **Download functionality** for generated code
- **Chat history** with conversation persistence

### 🔍 Knowledge Base Management
- **ChromaDB vector store** for B2Scala examples
- **Automatic document processing** from docs directory
- **Semantic search** across protocol implementations
- **Context-aware retrieval** for better code generation

## 🏗️ Project Structure

```
B2Scala-RAG-NVIDIA/
├── 📱 app.py                 # Main Streamlit application
├── ⚙️ config.py              # Centralized configuration
├── 🏃 run.py                 # Script runner utility
├── 🎓 train.py               # Knowledge base trainer
├── 🧪 example.py             # Usage example script
├── 📋 requirements.txt       # Python dependencies
├── � README.md              # Project documentation
├── 🚫 .gitignore             # Git ignore rules
│
├── 📂 src/                   # Source code modules
│   ├── 🔍 retriever.py       # RAG retrieval system
│   ├── 📊 data_processor.py  # Document processing
│   ├── 🔄 rag_pipeline.py    # Main RAG pipeline
│   ├── 📁 file_utils.py      # File upload utilities
│   └── 🔧 __init__.py        # Package initialization
│
├── 📂 docs/                  # Knowledge base documents
│   ├── 📄 *.pdf              # Protocol specifications
│   ├── 📝 *.txt              # B2Scala examples
│   └── 📖 *.md               # Documentation
│
├── 📂 examples/              # B2Scala protocol examples
│   ├── 🔐 bsc_modelling_emv.scala
│   ├── 🚀 bsc_modelling_quic.scala
│   ├── 🔒 bsc_modelling_tls_13.scala
│   ├── �️ bsc_modelling_kerberos.scala
│   └── � (18 total protocol examples)
│
├── 📂 data/                  # Input data files
├── 📂 generated/             # Generated outputs
└── 📂 kb/                    # ChromaDB knowledge base
    ├── chroma.sqlite3        # Vector database
    └── 📊 embeddings/        # Stored embeddings
```

## 🚀 Quick Start

### 1️⃣ Prerequisites

- **Python 3.13+**
- **NVIDIA API Key** (for AI endpoints) - See [API_KEY_SETUP.md](API_KEY_SETUP.md)
- **Tesseract OCR** (for image processing) - See [TESSERACT_SETUP.md](TESSERACT_SETUP.md)

### 2️⃣ Installation

```bash
# Clone the repository
git clone https://github.com/nizarrahmoun/B2Scala_RAG.git
cd B2Scala_RAG

# Install dependencies
pip install -r requirements.txt

# Set up your NVIDIA API key
cp .env.example .env
# Edit .env and add your NVIDIA API key
```

### 3️⃣ Initialize Knowledge Base

```bash
# Process documents and build the knowledge base
python train.py
```

### 4️⃣ Launch the Application

```bash
# Start the Streamlit app
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

## 💻 Usage Guide

### 🎯 Input Methods

#### 1. ✍️ Manual Text Input
Type your protocol description directly:
```
Title: Simple Key Exchange
Agents: Client, Server
Messages:
- Client -> Server: ClientHello(nonceC)
- Server -> Client: ServerHello(nonceS, cert)
- Client -> Server: Finished(MAC)
Goals: Mutual authentication, Establish session key
Assumptions: Server has certificate, Channel is unreliable
```

#### 2. 📁 File Upload
Upload various file formats:
- **PDF**: Protocol specifications and academic papers
- **Images**: Screenshots, diagrams, handwritten notes
- **Scala**: Existing B2Scala implementations

#### 3. 🔄 Combined Input
Upload a file and add additional instructions for modifications.

### 🛠️ Configuration Options

- **Number of retrieved documents**: 1-10 (default: 5)
- **API Key override**: Use custom NVIDIA API key
- **File size limit**: Maximum 10 MB per upload

## 🧬 Technical Architecture

### 🔧 Core Components

1. **RAGPipeline Class**
   - Orchestrates the entire generation process
   - Manages NVIDIA model interactions
   - Handles streaming responses with reasoning

2. **Retriever System**
   - NVIDIA embeddings for semantic search
   - ChromaDB for efficient vector storage
   - Context-aware document retrieval

3. **File Processing Pipeline**
   - PDF text extraction with PyPDF2
   - OCR processing with Tesseract
   - Scala source code parsing
   - Multi-encoding support

4. **Code Generation Engine**
   - Template-based B2Scala generation
   - Canonical example adherence
   - Syntax validation and error handling

### 🎯 Model Configuration

- **Embedding Model**: `nvidia/nv-embedqa-e5-v5`
- **Language Model**: `deepseek-ai/deepseek-v3.1`
- **Temperature**: 0.2 (focused, deterministic)
- **Top-p**: 0.7 (balanced creativity)
- **Max Tokens**: 8192 (comprehensive responses)

## 📊 Supported B2Scala Features

### 🏗️ Code Structure
- **Package declarations**: `bscala.bsc_program`
- **Standard imports**: B2Scala core libraries
- **Object definitions**: Protocol-specific objects
- **Section organization**: DATA, AGENTS, FORMULA & EXEC

### 🔐 Protocol Elements
- **Tokens and case classes**: Message definitions
- **Agent definitions**: Protocol participants
- **Communication patterns**: tell/get/ask operations
- **Security formulas**: Verification properties
- **Execution framework**: BSC_Runner_BHM

### 📚 Example Protocols
- **TLS 1.3**: Transport Layer Security
- **QUIC**: Modern transport protocol
- **EMV**: Payment card transactions
- **Kerberos**: Authentication protocol
- **Needham-Schroeder**: Classic key exchange

## 🔧 Development

### 🧪 Testing

```bash
# Test with sample protocol
python example.py

# Upload test_sample.scala to verify Scala processing
# Use the web interface to test various input methods
```

### 🛠️ Adding New Protocols

1. Add protocol documents to `docs/` directory
2. Run `python train.py` to update knowledge base
3. Test generation through the web interface

### 🔍 Debugging

- Check terminal output for detailed error messages
- Verify NVIDIA API key configuration
- Ensure Tesseract is properly installed for OCR
- Review ChromaDB logs for retrieval issues

## 📋 Dependencies

### 🐍 Core Python Packages
- `streamlit==1.30.0` - Web interface framework
- `langchain==0.1.0` - LLM integration framework
- `langchain-nvidia-ai-endpoints==0.0.8` - NVIDIA API integration
- `chromadb==0.4.20` - Vector database
- `PyPDF2==3.0.1` - PDF processing

### 🖼️ File Processing
- `Pillow>=11.2.1` - Image processing
- `pytesseract>=0.3.13` - OCR text extraction
- `pdf2image>=1.17.0` - PDF to image conversion

### 📊 Data Processing
- `numpy==1.24.3` - Numerical computations
- `pandas==2.0.3` - Data manipulation
- `python-dotenv==1.0.0` - Environment management

## 🚨 Troubleshooting

### Common Issues

1. **NVIDIA API Key Errors**
   - Verify API key is valid and has sufficient credits
   - Check network connectivity
   - Try using the default provided key

2. **OCR Not Working**
   - Install Tesseract OCR: See [TESSERACT_SETUP.md](TESSERACT_SETUP.md)
   - Verify PATH configuration
   - Test with high-contrast images

3. **Knowledge Base Empty**
   - Run `python train.py` to build the knowledge base
   - Ensure documents exist in `docs/` directory
   - Check ChromaDB permissions

4. **Streamlit Errors**
   - Update Streamlit: `pip install --upgrade streamlit`
   - Clear browser cache
   - Check port availability (default: 8501)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **NVIDIA** for providing powerful AI endpoints
- **DeepSeek** for the advanced language model
- **B2Scala** community for protocol examples
- **Streamlit** for the excellent web framework
- **ChromaDB** for efficient vector storage

## 📞 Support

For questions, issues, or suggestions:

1. **Create an issue** on GitHub
2. **Check existing documentation** in the `docs/` folder
3. **Review troubleshooting** section above
4. **Test with sample inputs** provided

---

