# src-backend/llm_interface.py
import os
import base64
from typing import List, Tuple
from llama_cpp import Llama
import httpx

# --- Import our new Agent classes ---
from agents.ollama_client import OllamaClient
from agents.vibe_detector import VibeDetector

# --- Global State for our AI Models ---
# This is a best practice for managing resources in a FastAPI app
# They will be initialized once during the application's lifespan.
llm_local: Llama | None = None
ollama_client: OllamaClient | None = None
vibe_detector: VibeDetector | None = None
ollama_is_available: bool = False

# --- Configuration ---
LOCAL_MODEL_FILENAME = "tinyllama-1.1b-chat-v1.0.Q3_K_S.gguf"
# Assumes a 'models' folder in the root of your project, outside src-backend
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
LOCAL_MODEL_PATH = os.path.join(MODELS_DIR, LOCAL_MODEL_FILENAME)


# --- Lifespan Functions (to be called from main.py) ---
async def initialize_llm_clients():
    """
    Called once when the application starts.
    Loads the local Llama model and probes for the advanced Ollama service.
    """
    global llm_local, ollama_client, vibe_detector, ollama_is_available

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


# --- THE UPGRADED CORE FUNCTION ---
async def get_llm_response(prompt: str, image_bytes: bytes | None, history: List[Tuple]) -> str:
    """
    The single point of entry for getting a response from an LLM.
    Acts as the intelligent router for our "Progressive Sovereignty" architecture.
    """
    # --- Intelligent Router Logic ---
    if image_bytes:
        # ALL multimodal requests go to the Ollama brain
        if not ollama_client or not ollama_is_available:
            return "Error: Vision features are not enabled. Please ensure Ollama is running."
        
        print("🧠 Routing to Advanced Brain for multimodal input...")
        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # We will build a more sophisticated history formatter later
        # For now, we just use the latest prompt and image
        messages = [{'role': 'user', 'content': prompt, 'images': [img_base64]}]
        
        response = await ollama_client.chat(
            model='llava:latest',
            messages=messages
        )
        return response['message']['content']

    elif ollama_is_available and vibe_detector and ollama_client:
        # If Ollama is available, use the advanced conversational brain for text too
        print("🧠 Routing to Advanced Brain for text input...")
        vibe = await vibe_detector.classify(prompt)
        
        # Format history for Ollama
        messages = []
        for actor, content in history:
            # We assume the last turn is the current user prompt, which we'll add now
            if actor != 'user' or content != prompt:
                messages.append({'role': actor if actor == 'user' else 'assistant', 'content': content})
        
        messages.append({'role': 'user', 'content': f"({vibe.upper()} VIBE) {prompt}"})
        
        response = await ollama_client.chat(model='llama3:latest', messages=messages)
        return response['message']['content']
    
    else:
        # Fallback to the simple, sovereign, local text brain
        if not llm_local:
            return "Error: Local text model is not available."
            
        print("🧠 Routing to Sovereign Language Brain...")
        # Simple history formatting for the local model
        history_str = "\n".join([f"<|{turn[0]}|>\n{turn[1]}" for turn in history])
        prompt_template = f"<|system|>\nYou are a helpful AI assistant named Wise.\n{history_str}<|user|>\n{prompt}\n<|assistant|>\n"
        
        output = llm_local(prompt_template, max_tokens=300, stop=["<|user|>", "<|system|>"])
        return output["choices"][0]["text"].strip()