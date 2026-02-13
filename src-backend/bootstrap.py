# src-backend/bootstrap.py
import subprocess
import sys
import os
import requests

# --- Configuration ---
# Llama-3.2-1B-Instruct (4-bit Quantized GGUF) - ~700MB
MODEL_URL = "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
MODEL_FILENAME = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"

# This path goes UP one level from src-backend to the project root, then into 'models'
# This ensures it matches the path in llm_interface.py
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

REQUIREMENTS_FILE = "requirements.txt"

def run_command(command):
    """Runs a command and checks for errors, exiting if it fails."""
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("--- ERROR ---")
        print(f"Command failed: {' '.join(command)}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        sys.exit(1)

print("--- Bootstrapping Engelbert Kernel ---")

# 1. Install Python dependencies from our official list
print(f"📦 Installing Python packages from {REQUIREMENTS_FILE}...")
run_command([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
print("✅ Dependencies installed.")

# 2. Download the model
print("\n🧠 Checking for language model...")
os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.exists(MODEL_PATH):
    print(f"Downloading {MODEL_FILENAME} (~600MB)... This may take a few minutes.")
    try:
        with requests.get(MODEL_URL, stream=True) as r:
            r.raise_for_status()
            with open(MODEL_PATH, 'wb') as f:
                content_length = r.headers.get('content-length')
                total_length = int(content_length) if content_length is not None else None
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ Model downloaded successfully to {MODEL_PATH}")
    except requests.exceptions.RequestException as e:
        print(f"--- ERROR ---")
        print(f"Failed to download model: {e}")
        sys.exit(1)
else:
    print(f"✅ Model '{MODEL_FILENAME}' already exists.")

print("\n🎉 Bootstrap complete! The backend is ready to run.")
print("➡️ Next step: Run 'uvicorn main:app --reload'")