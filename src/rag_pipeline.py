from retriever import Retriever
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os
import sys

class RAGPipeline:
    def __init__(self, k=3, api_key=None):
        self.retriever = Retriever(k=k, api_key=api_key)
        
        # Initialize NVIDIA ChatNVIDIA model
        self.llm = ChatNVIDIA(
            model="deepseek-ai/deepseek-v3.1",
            api_key=api_key or "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",
            temperature=0.2,
            top_p=0.7,
            max_tokens=8192,
            extra_body={"chat_template_kwargs": {"thinking": True}},
        )
    
    def load_structured_draft(self, file_path):
        """
        Loads a structured protocol draft from a text file.
        Includes error handling for file operations.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Draft file '{file_path}' not found.", file=sys.stderr)
            return None
        except Exception as e:
            print(f"An unexpected error occurred while reading the file: {e}", file=sys.stderr)
            return None

    def generate_answer(self, draft):
        # Step 1: Retrieve context
        try:
            context_chunks = self.retriever.get_context(draft)
            context_text = "\n".join(context_chunks)
        except Exception as e:
            print(f"Error during context retrieval: {e}", file=sys.stderr)
            return None, []

        # Step 2: Build prompt
        prompt = f"""
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

        # Step 3: Call LLM with streaming
        print("🔹 Generating answer with NVIDIA LLM...")
        try:
            response_content = ""
            
            # Use streaming to capture both reasoning and content
            for chunk in self.llm.stream([{"role": "user", "content": prompt}]):
                # Handle reasoning content if available
                if chunk.additional_kwargs and "reasoning_content" in chunk.additional_kwargs:
                    print(chunk.additional_kwargs["reasoning_content"], end="")
                
                # Add content to response
                if chunk.content:
                    response_content += chunk.content
                    print(chunk.content, end="")
            
            return response_content, context_chunks
        except Exception as e:
            print(f"Error calling LLM: {e}", file=sys.stderr)
            return None, context_chunks

if __name__ == "__main__":
    draft_file = "../data/structured_draft.txt"
    output_file = os.path.join("../generated", "generated_code.scala")
    
    # Initialize with API key
    api_key = "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"
    rag = RAGPipeline(k=5, api_key=api_key)

    # Load the structured draft with error handling
    protocol_draft = rag.load_structured_draft(draft_file)
    if not protocol_draft:
        sys.exit(1)

    answer, context = rag.generate_answer(protocol_draft)

    # Check if a valid answer was returned before proceeding
    if answer is None:
        print("Code generation failed. Exiting.", file=sys.stderr)
        sys.exit(1)

    print("\n--- Retrieved Context ---")
    try:
        with open("../data/context.txt", "w", encoding="utf-8") as file:
            for c in context:
                file.write(str(c) + "\n---\n")
    except Exception as e:
        print(f"Failed to write context file: {e}", file=sys.stderr)

    print("\n--- Generated Answer ---")
    try:
        os.makedirs("../generated", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(answer)
        print("Code generation successful. Check the 'generated' directory.")
    except Exception as e:
        print(f"Failed to write generated code file: {e}", file=sys.stderr)
