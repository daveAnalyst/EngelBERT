import time
import random
import asyncio
import psutil
from datetime import datetime

# --- Import Core Services ---
from llm_interface import generate_insight
# We reuse the logic from memory_service to talk to LanceDB
from memory_service import MemoryService

# --- Configuration ---
DREAM_INTERVAL_SECONDS = 30  # How often to check for connections
MIN_CONFIDENCE_THRESHOLD = 0.75

def can_dream() -> bool:
    """
    Resource Guard: Returns True only if the system is idle enough.
    Re-implemented here for the standalone worker process.
    """
    try:
        # Get Stats
        ram_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Print stats so we can see them in the terminal
        print(f"   [System Status] RAM: {ram_percent}% | CPU: {cpu_percent}%")

        # 1. Check RAM (Relaxed to 96% for testing)
        if ram_percent > 96:
            print("   ⚠️ RAM too high to dream.")
            return False

        # 2. Check CPU (Relaxed to 90% for testing)
        if cpu_percent > 90:
            print("   ⚠️ CPU too high to dream.")
            return False
            
        return True
    except Exception as e:
        print(f"Scheduler Error: {e}")
        return False

def dream_loop():
    """
    The Main Loop. This runs forever in the background.
    """
    print("🌙 Dream Cycle Worker Started. Watching for latent connections...")
    
    # Initialize Memory
    memory = MemoryService()
    
    while True:
        try:
            # 1. Resource Check
            if not can_dream():
                print("💤 System busy. Sleeping for 60s...")
                time.sleep(60)
                continue

            # 2. The Logic: Find a random "Seed" thought
            print("✨ Dreaming: Scanning Semantic Memory...")
            
            # Pick a random topic to "dream" about
            seed_concepts = ["intelligence", "network", "energy", "optimization"]
            concept = random.choice(seed_concepts)
            
            print(f"   ... Thinking about '{concept}'")
            
            # Query LanceDB
            results = memory.find_relevant_chunks(concept, top_k=2)
            
            # --- THIS IS THE NEW LOGIC BLOCK ---
            if len(results) >= 2:
                note_a = results[0]['text']
                note_b = results[1]['text']
                
                # Filter out the dummy "test" row if it appears
                #if note_a == "test" or note_b == "test":
                #    print("   ... Skipped dummy test data.")
                #    time.sleep(1) # Short pause
                #    continue

                print(f"\n   🔗 Connecting concepts...")
                print(f"   A: {note_a[:40]}...")
                print(f"   B: {note_b[:40]}...")
                
                # --- THE MOMENT OF TRUTH ---
                # This calls the Llama 3.2 model via the new function we added
                insight = generate_insight(note_a, note_b)
                
                print(f"   💡 INSIGHT GENERATED: {insight}\n")
                
                # --- NEW: SAVE TO MEMORY ---
                if "No Connection" not in insight:
                    memory.log_insight(note_a, note_b, insight)
            else:
                print("   ... No strong connections found.")
            
            time.sleep(DREAM_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("🛑 Dream Cycle stopped by user.")
            break
        except Exception as e:
            print(f"❌ Dream Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    dream_loop()