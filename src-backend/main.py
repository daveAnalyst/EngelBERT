# src-backend/main.py
import psutil 
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from contextlib import asynccontextmanager

# --- Core Engelbert Services ---
from llm_interface import get_llm_response, initialize_llm_clients, close_llm_clients
from memory_service import MemoryService

# --- Global State ---
memory_service = None

# added can dream function
def can_dream() -> bool:
    """
    Adaptive Scheduler: Returns True only if the system has resources to spare.
    Prevents the background worker from crashing the user's laptop.
    """
    try:
        # 1. Check RAM (If usage > 80%, STOP)
        ram_percent = psutil.virtual_memory().percent
        if ram_percent > 80:
            print(f"💤 Dreaming paused: High RAM usage ({ram_percent}%)")
            return False

        # 2. Check CPU (If usage > 70%, STOP)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > 70:
            print(f"💤 Dreaming paused: High CPU usage ({cpu_percent}%)")
            return False
            
        return True
    except Exception as e:
        print(f"⚠️ Scheduler Error: {e}")
        return False # Fail safe

# --- FastAPI Lifespan Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global memory_service
    print("--- Starting Engelbert Kernel (V2 with Memory) ---")
    
    # THE 'AWAIT' FIX IS HERE
    await initialize_llm_clients() 
    print("✅ LLM Interface is online.")

    # Initialize our Memory Service
    memory_service = MemoryService()
    print("✅ Memory Service is online.")

     # NOW, initialize the LLM clients
    await initialize_llm_clients() 
    print("✅ LLM Interface is online.")

    yield # --- Application runs here ---

    print("--- Shutting down Engelbert Kernel ---")
    await close_llm_clients()
    if memory_service:
        memory_service.close_connection()

# --- FastAPI App Definition ---
app = FastAPI(lifespan=lifespan, title="Engelbert OS Kernel")

origins = ["http://localhost:3000", "tauri://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Hello from the Python backend!"}

@app.post("/api/v1/chat")
async def chat_endpoint(
    prompt: Annotated[str, Form()], 
    session_id: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None
):
    if not memory_service:
        raise HTTPException(status_code=503, detail="Memory service is not available.")

    current_session_id = session_id if session_id else str(uuid.uuid4())
    
    memory_service.add_log_entry(
        session_id=current_session_id, 
        actor="user", 
        content=prompt
    )
    
    history = memory_service.get_recent_history(current_session_id, limit=10)
    
    image_bytes = await image.read() if image else None
    
    # THE 'HISTORY' ARGUMENT FIX IS HERE
    llm_response = await get_llm_response(prompt, image_bytes, history)
    
    memory_service.add_log_entry(
        session_id=current_session_id, 
        actor="ai", 
        content=llm_response
    )
    
    return {"response": llm_response, "session_id": current_session_id}