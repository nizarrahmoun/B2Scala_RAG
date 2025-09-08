"""
Configuration file for B2Scala-RAG-NVIDIA
"""

import os

# NVIDIA API Configuration
NVIDIA_API_KEY = ""          """connect to nvidia to get your own api (deepseek 3.1)"""

# Model Configuration
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"
CHAT_MODEL = "deepseek-ai/deepseek-v3.1"

# Model Parameters
TEMPERATURE = 0.2
TOP_P = 0.7
MAX_TOKENS = 8192
ENABLE_REASONING = True

# Directory Configuration
KB_DIR = "./kb"
DOCS_DIR = "./docs"
DATA_DIR = "./data"
GENERATED_DIR = "./generated"
EXAMPLES_DIR = "./examples"

# ChromaDB Configuration
COLLECTION_NAME = "b2scala_knowledge"

# Text Splitting Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
SEPARATORS = ["\n\n", "\n", ";", ".", " "]

# Retrieval Configuration
DEFAULT_K = 5  # Number of documents to retrieve

# Streamlit Configuration
PAGE_TITLE = "B2Scala Code Generator (NVIDIA)"
PAGE_ICON = "📝"

def get_nvidia_api_key():
    """Get NVIDIA API key from environment or use default."""
    return os.getenv("NVIDIA_API_KEY", NVIDIA_API_KEY)

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [KB_DIR, DOCS_DIR, DATA_DIR, GENERATED_DIR, EXAMPLES_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# B2Scala Code Template
B2SCALA_TEMPLATE = """package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** {protocol_description} */
object BSC_modelling_{protocol_name} extends App {{

  /////////////////////////////  DATA  /////////////////////////////
  
  // Tokens for agents
  {agent_tokens}
  
  // Protocol-specific tokens and case classes
  {data_definitions}

  /////////////////////////////  AGENTS  /////////////////////////////
  
  {agent_definitions}

  /////////////////////////////  FORMULA & EXEC  /////////////////////////////
  
  val Protocol = Agent {{ {agent_composition} }}
  
  val F: BHM_Formula = bHM {{ {formula_definition} }}
  
  val runner = new BSC_Runner_BHM
  runner.execute(Protocol, F)
}}
"""

# Prompt Template for Code Generation
GENERATION_PROMPT = """
You are an expert in protocol modeling and B2Scala.
You have access to a Knowledge Base which contains canonical, working B2Scala examples.
One canonical example in the Knowledge Base is the QUIC v1 handshake file that uses the exact
package, imports, object structure, DATA / AGENTS / FORMULA & EXEC sections, and B2Scala primitives
shown below. Use that example as the authoritative template and style guide.

Your tasks (MANDATORY):
1) Read the given protocol draft (variable `draft` below) and the Knowledge Base context (variable `context_text`).
2) Summarize the draft internally (agents, messages, goals, assumptions) and then produce a single output:
- Exactly one Scala source file, and nothing else (no extra prose).
- The Scala file MUST follow the package, imports, object name, and structural layout shown in the canonical example.
- All tokens, case classes, agents, messages and formulas MUST be adapted from the draft but preserve the canonical coding style.
3) If any detail in the draft is missing, make reasonable assumptions and document them with inline // comments in the Scala file.
4) Ensure the Scala file is self-contained (all needed case classes and Tokens declared) and is syntactically consistent with the canonical QUIC example from the Knowledge Base.
5) Do NOT output anything outside the Scala file. The entire assistant response must be the file contents only.

RESTRICTIONS (must obey):
- Use **exactly** this package and imports header at the top of the file:
package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

- Follow the canonical section headings and layout: DATA, AGENTS, FORMULA & EXEC as in the example.
- Preserve naming style: Tokens named with quotes like Token("Name"), SI_Term case classes, Agent scripts using tell/get/ask composition, and final execution via new BSC_Runner_BHM().execute(Protocol, F).
- Produce case classes for all structured terms you need (messages, crypto, envelopes, events, etc.).
- All assumptions must be inline commented with // and briefly justified.
- Output must be a compilable B2Scala program using core primitives only (no external libraries beyond the imports above).

VERY IMPORTANT OUTPUT RULE:
- The assistant MUST output a single Scala file only, using the object name `BSC_modelling_<ProtocolNameNoSpaces>` where <ProtocolNameNoSpaces> is derived from the draft title (remove spaces, punctuation).
- Include a one-line doc comment right after the imports briefly describing the protocol.

Input variables available:
- draft: the protocol draft text (use to extract agents, messages, goals, assumptions).
{draft}
- context_text: Knowledge Base context (contains canonical B2Scala examples you MUST follow).
{context_text}
Now produce the Scala file ONLY, using the canonical QUIC example style from the Knowledge Base as the template and adapting tokens/messages/agents from the draft. Ensure all missing details are commented with // assumptions.
"""
