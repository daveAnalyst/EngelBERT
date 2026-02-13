# src-backend/llm_interface.py
import os
import base64
from typing import List, Tuple
from llama_cpp import Llama
import httpx

# --- Core Engelbert Services ---
from agents.ollama_client import OllamaClient
from agents.vibe_detector import VibeDetector
from memory_service import MemoryService

# --- Global State for our AI Models & Services ---
llm_local: Llama | None = None
ollama_client: OllamaClient | None = None
vibe_detector: VibeDetector | None = None
ollama_is_available: bool = False
memory_service: MemoryService | None = None

# --- Configuration ---
LOCAL_MODEL_FILENAME = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
LOCAL_MODEL_PATH = os.path.join(MODELS_DIR, LOCAL_MODEL_FILENAME)


# --- Lifespan Functions (to be called from main.py) ---
async def initialize_llm_clients(mem_service: MemoryService):
    """
    Called once when the application starts.
    Loads models and accepts the memory_service instance.
    """
    global llm_local, ollama_client, vibe_detector, ollama_is_available, memory_service
    
    memory_service = mem_service
    
    # 1. ALWAYS load the local text engine.
    if os.path.exists(LOCAL_MODEL_PATH):
        print(f"🧠 Loading local 'Language Brain': {LOCAL_MODEL_FILENAME}...")
        try:
            llm_local = Llama(model_path=LOCAL_MODEL_PATH, n_ctx=2048, n_gpu_layers=-1, verbose=False)
            print("✅ 'Language Brain' is online.")
        except Exception as e:
            print(f"❌ Error loading local model: {e}")
    else:
        print(f"⚠️ Warning: Local model not found at {LOCAL_MODEL_PATH}. Sovereign text mode will be disabled.")

    # 2. CHECK for the advanced Ollama-powered brain.
    print("🔬 Probing for local Ollama service...")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.get("http://127.0.0.1:11434")
        ollama_is_available = True
        
        ollama_client = OllamaClient()
        vibe_detector = VibeDetector(ollama_client)
        
        print("✅ 'Advanced Brain' (Ollama) detected. Enhanced features enabled.")
    except httpx.RequestError:
        print("ℹ️ Ollama not found. Running in sovereign text-only mode.")
        ollama_is_available = False

async def close_llm_clients():
    """Called once when the application shuts down."""
    if ollama_client:
        await ollama_client.close()
    print("LLM clients closed.")


# --- THE FINAL, RAG-ENABLED CORE FUNCTION ---
async def get_llm_response(prompt: str, image_bytes: bytes | None, history: List[Tuple]) -> str:
    """
    The single point of entry for getting a response from an LLM.
    It performs a semantic search to augment the prompt with relevant context.
    """
    global memory_service
    if not memory_service:
        return "Error: Memory service is not available in the LLM interface."

    # --- Step 1: AUGMENT with Semantic Memory (The RAG Step) ---
    print("🧠 Augmenting prompt with semantic memory...")
    relevant_chunks = memory_service.find_relevant_chunks(prompt, top_k=3)
    
    context_str = ""
    if relevant_chunks:
        print(f"✅ Found {len(relevant_chunks)} relevant chunks from the Second Brain.")
        context_sources = list(set([chunk['source_id'] for chunk in relevant_chunks]))
        context_str = "--- Relevant Context from your Second Brain ---\n"
        for chunk in relevant_chunks:
            context_str += f"- {chunk['text']}\n"
        context_str += f"Sources: {', '.join(context_sources)}\n----------------------------------------\n\n"
    else:
        print("ℹ️ No highly relevant chunks found in the Second Brain for this query.")
    
    # --- Step 2: Intelligent Router Logic ---

    # --- ROUTE 1: Multimodal requests (Ollama) ---
    if image_bytes:
        if not ollama_client or not ollama_is_available:
            return "Error: Vision features are not enabled. Please ensure Ollama is running."
        
        print("🧠 Routing to Advanced Brain for multimodal input...")
        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # We add the RAG context to the multimodal prompt as well
        final_prompt = f"{context_str}User query: {prompt}"
        messages = [{'role': 'user', 'content': final_prompt, 'images': [img_base64]}]
        
        response = await ollama_client.chat(model='llava:latest', messages=messages)
        return response['message']['content']

    # --- ROUTE 2: Advanced text requests (Ollama) ---
    elif ollama_is_available and vibe_detector and ollama_client:
        print("🧠 Routing to Advanced Brain for text input...")
        vibe = await vibe_detector.classify(prompt)
        
        messages = []
        # We prepend our RAG context as the first "system" message for Ollama
        if context_str:
            messages.append({'role': 'system', 'content': context_str})
            
        for actor, content in history:
            if actor != 'user' or content != prompt:
                messages.append({'role': actor if actor == 'user' else 'assistant', 'content': content})
        
        messages.append({'role': 'user', 'content': f"({vibe.upper()} VIBE) {prompt}"})
        
        response = await ollama_client.send_chat(model='llama3:latest', messages=messages)
        return response['message']['content']
    
    # --- ROUTE 3: Sovereign text requests (Local Llama) ---
    else:
        if not llm_local:
            return "Error: Local text model is not available."
        print("🧠 Routing to Sovereign Language Brain (Llama 3.2) with context...")
    
    # Llama 3 format: <|start_header_id|>role<|end_header_id|>\n\ntext<|eot_id|>
    
    system_prompt = (
        "You are Wise, a helpful AI assistant. "
        "Use the provided context to answer the user's question. "
        "If the context isn't relevant, ignore it."
    )
    
    # Build the context block
    full_context = ""
    if context_str:
        full_context = f"Context from Second Brain:\n{context_str}\n\n"

    # Construct the Llama 3 Prompt
    prompt_str = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>"
    
    # Add History
    for actor, content in history:
        role = "assistant" if actor == "ai" else "user"
        prompt_str += f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>"
        
    # Add Current Turn (with RAG context injected)
    prompt_str += f"<|start_header_id|>user<|end_header_id|>\n\n{full_context}{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    
    output = llm_local(prompt_str, max_tokens=512, stop=["<|eot_id|>"])
    return output["choices"][0]["text"].strip()