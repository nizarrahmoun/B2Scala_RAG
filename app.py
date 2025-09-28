import streamlit as st
import sys
import os
from src.retriever import Retriever
from src.file_utils import process_uploaded_file, validate_file_size, get_file_type_icon
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from config import NVIDIA_API_KEY

class RAGPipeline:
    def __init__(self, k=3, api_key=None):
        try:
            # Initialize Retriever with NVIDIA embeddings
            self.retriever = Retriever(k=k, api_key=api_key)
            
            # Initialize NVIDIA ChatNVIDIA model
            self.llm = ChatNVIDIA(
                model="deepseek-ai/deepseek-v3.1",
                api_key=api_key or NVIDIA_API_KEY,
                temperature=0.2,
                top_p=0.7,
                max_tokens=8192,
                extra_body={"chat_template_kwargs": {"thinking": True}},
            )
        except Exception as e:
            st.error(f"Error initializing RAGPipeline components: {e}")
            st.stop()

    def generate_answer(self, draft, show_streaming=True, show_reasoning=False):
        # Step 1: Retrieve context
        try:
            context_chunks = self.retriever.get_context(draft)
            context_text = "\n".join(context_chunks)
        except Exception as e:
            st.error(f"Error during context retrieval: {e}")
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
        st.info("🔹 Generating answer with NVIDIA LLM...")
        try:
            response_content = ""
            
            # Create placeholders only if needed
            response_placeholder = st.empty() if show_streaming else None
            reasoning_placeholder = st.empty() if show_reasoning else None
            
            # Use streaming to capture both reasoning and content
            for chunk in self.llm.stream([{"role": "user", "content": prompt}]):
                # Handle reasoning content if available and requested
                if show_reasoning and chunk.additional_kwargs and "reasoning_content" in chunk.additional_kwargs:
                    reasoning_content = chunk.additional_kwargs["reasoning_content"]
                    if reasoning_placeholder:
                        with reasoning_placeholder.container():
                            st.caption("🤔 Model Reasoning:")
                            st.text(reasoning_content)
                
                # Add content to response
                if chunk.content:
                    response_content += chunk.content
                    # Update the streaming display only if enabled
                    if show_streaming and response_placeholder:
                        with response_placeholder.container():
                            st.code(response_content, language="scala")
            
            # Clear placeholders after completion if streaming was shown
            if show_streaming and response_placeholder:
                response_placeholder.empty()
            if show_reasoning and reasoning_placeholder:
                reasoning_placeholder.empty()
            
            return response_content, context_chunks
        except Exception as e:
            st.error(f"Error calling NVIDIA LLM: {e}")
            return None, context_chunks

# --- Streamlit App ---

st.set_page_config(page_title="B2Scala Code Generator (NVIDIA)", page_icon="📝")

st.title("B2Scala Code Generator Chatbot")
st.caption("A RAG-powered assistant using NVIDIA AI endpoints to formalize protocol drafts into B2Scala.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Key input (optional override)
    api_key_input = st.text_input(
        "NVIDIA API Key (optional override)", 
        value="", 
        type="password",
        help="Leave empty to use default API key"
    )
    
    # Number of retrieved documents
    k_value = st.slider("Number of retrieved documents", min_value=1, max_value=10, value=5)
    
    # Model parameters
    st.subheader("Model Parameters")
    st.text("Model: deepseek-ai/deepseek-v3.1")
    st.text("Temperature: 0.2")
    st.text("Top-p: 0.7")
    st.text("Max Tokens: 8192")
    
    # Display options
    st.subheader("Display Options")
    show_streaming = st.checkbox("Show streaming response", value=True, help="Display code as it's being generated")
    show_reasoning = st.checkbox("Show model reasoning", value=False, help="Display the model's thinking process")
    
    # File upload section
    st.subheader("📁 File Upload")
    st.markdown("Upload PDF documents, images, or Scala files containing protocol drafts:")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'scala'],
        help="Supported formats: PDF, PNG, JPG, JPEG, BMP, TIFF, SCALA"
    )
    
    # Process uploaded file
    if uploaded_file is not None:
        if validate_file_size(uploaded_file, max_size_mb=10):
            file_icon = get_file_type_icon(uploaded_file.type, uploaded_file.name)
            with st.spinner(f"Processing {file_icon} {uploaded_file.name}..."):
                extracted_text = process_uploaded_file(uploaded_file)
                
            if extracted_text:
                st.success(f"✅ File processed successfully!")
                
                # Show appropriate preview based on file type
                if uploaded_file.name.lower().endswith('.scala'):
                    st.markdown("**Scala Code Preview (first 1000 characters):**")
                    st.code(
                        extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text,
                        language="scala"
                    )
                else:
                    st.text_area(
                        "Extracted Text Preview", 
                        extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                        height=100,
                        help="First 500 characters of extracted text"
                    )
                
                # Store extracted text in session state
                st.session_state.uploaded_text = extracted_text
                st.session_state.uploaded_filename = uploaded_file.name
                st.session_state.uploaded_file_type = uploaded_file.type
            else:
                st.error("❌ Failed to extract text from file")
    
    # Clear uploaded content button
    if hasattr(st.session_state, 'uploaded_text'):
        if st.button("🗑️ Clear Uploaded Content"):
            del st.session_state.uploaded_text
            if hasattr(st.session_state, 'uploaded_filename'):
                del st.session_state.uploaded_filename
            st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display uploaded file info if available
if hasattr(st.session_state, 'uploaded_text'):
    file_icon = get_file_type_icon(
        getattr(st.session_state, 'uploaded_file_type', ''), 
        st.session_state.uploaded_filename
    )
    st.info(f"{file_icon} **Uploaded file:** {st.session_state.uploaded_filename}")
    
    with st.expander("View uploaded content"):
        if st.session_state.uploaded_filename.lower().endswith('.scala'):
            st.code(st.session_state.uploaded_text, language="scala")
        else:
            st.text_area(
                "Full extracted text",
                st.session_state.uploaded_text,
                height=200
            )

# Input method selection
st.subheader("💬 Input Method")
input_method = st.radio(
    "Choose how to provide your protocol draft:",
    ["✍️ Type manually", "📁 Use uploaded file", "🔄 Combine both"],
    horizontal=True
)

# Handle different input methods
user_input = ""

if input_method == "✍️ Type manually":
    user_input = st.chat_input("Enter your protocol draft here...")
    
elif input_method == "📁 Use uploaded file":
    if hasattr(st.session_state, 'uploaded_text'):
        if st.button("🚀 Generate B2Scala code from uploaded file"):
            user_input = st.session_state.uploaded_text
    else:
        st.warning("Please upload a file first using the sidebar.")
        
elif input_method == "🔄 Combine both":
    if hasattr(st.session_state, 'uploaded_text'):
        additional_text = st.text_area(
            "Add additional instructions or modifications:",
            placeholder="You can add specific requirements, modifications, or additional context here..."
        )
        if st.button("🚀 Generate B2Scala code with combined input"):
            user_input = f"""
Uploaded file content:
{st.session_state.uploaded_text}

Additional instructions:
{additional_text}
"""
    else:
        st.warning("Please upload a file first using the sidebar.")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.code(message["content"], language="scala")
        else:
            st.markdown(message["content"])

# Process user input (from any method)
if user_input:
    # Add user message to chat history
    display_input = user_input[:200] + "..." if len(user_input) > 200 else user_input
    st.session_state.messages.append({"role": "user", "content": display_input})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        if len(user_input) > 500:
            with st.expander("View full input"):
                st.markdown(user_input)
            st.markdown(f"**Input preview:** {display_input}")
        else:
            st.markdown(user_input)

    # Instantiate the RAG pipeline
    api_key = api_key_input if api_key_input else NVIDIA_API_KEY
    rag_pipeline = RAGPipeline(k=k_value, api_key=api_key)

    # Get the code generation response
    with st.chat_message("assistant"):
        with st.spinner("Generating B2Scala code with NVIDIA AI..."):
            answer, context = rag_pipeline.generate_answer(user_input, show_streaming, show_reasoning)
        
        if answer:
            # Display the generated code (only if streaming wasn't shown)
            if not show_streaming:
                st.code(answer, language="scala")
            else:
                # Show a final clean version
                st.markdown("**Final Generated Code:**")
                st.code(answer, language="scala")
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # Option to download the generated code
            st.download_button(
                label="Download Generated Code",
                data=answer,
                file_name="generated_b2scala_code.scala",
                mime="text/plain"
            )
            
            # Show retrieved context in expander
            with st.expander("📚 Retrieved Context"):
                for i, ctx in enumerate(context, 1):
                    st.text_area(f"Context {i}", ctx, height=100)
        else:
            st.warning("Could not generate code. Please check your NVIDIA API key and connection.")

# Instructions section
with st.expander("📖 How to use"):
    st.markdown("""
    ## Input Methods
    
    ### 1. 📝 Manual Text Input
    - Type your protocol draft directly in the chat input
    - Include agents, messages, security goals, and assumptions
    
    ### 2. 📁 File Upload
    - Upload PDF documents, images, or Scala files containing protocol drafts
    - Supported formats: PDF, PNG, JPG, JPEG, BMP, TIFF, SCALA
    - Maximum file size: 10 MB
    - For images, OCR (Optical Character Recognition) will extract text
    - For Scala files, the source code will be read directly
    
    ### 3. 🔄 Combined Input
    - Upload a file and add additional instructions
    - Perfect for modifying or extending existing protocols
    
    ## Process Flow
    1. **Choose input method** (manual, file upload, or combined)
    2. **Provide your protocol information** including:
       - Agents involved (e.g., Client, Server)
       - Messages exchanged
       - Security goals
       - Any assumptions
    3. **Click send/generate** and the system will:
       - Retrieve relevant B2Scala examples from the knowledge base
       - Generate B2Scala code using NVIDIA's DeepSeek model
       - Show the reasoning process (if available)
    4. **Download** the generated code using the download button
    
    ## Example Manual Input
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
    
    ## File Upload Tips
    - **PDFs**: Best for formal protocol specifications
    - **Images**: Good for handwritten notes or diagrams with text
    - **Scala Files**: Perfect for existing B2Scala protocol implementations
    - **OCR Quality**: Clear, high-contrast text works best for images
    - **File Size**: Keep under 10 MB for optimal processing speed
    - **Scala Use Cases**: Upload existing protocols to modify, extend, or analyze
    """)

# Footer
st.markdown("---")
st.markdown("**B2Scala-RAG")
st.caption("📁 File Upload Support: PDF, PNG, JPG, JPEG, BMP, TIFF, SCALA | 🔍 OCR Text Extraction")
