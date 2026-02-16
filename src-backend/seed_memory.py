from memory_service import MemoryService
import time

def seed_brain():
    print("🌱 Seeding the Brain with dummy memories...")
    mem = MemoryService()
    
    # 1. Topic A: Biology (The "Nature" Cluster)
    biology_notes = [
        "The mycelial network allows trees to communicate underground.",
        "Neural networks in the human brain strengthen via repetition (Hebbian learning).",
        "Ant colonies exhibit swarm intelligence without a central commander.",
        "Evolutionary algorithms mimic natural selection to optimize code.",
        "Photosynthesis converts light into chemical energy, similar to solar panels."
    ]
    
    # 2. Topic B: Tech/Architecture (The "System" Cluster)
    tech_notes = [
        "Distributed systems require consensus algorithms like Raft or Paxos.",
        "The internet is a decentralized network of nodes, much like a forest.",
        "Optimization in AI often gets stuck in local minima.",
        "Solar energy storage is the bottleneck for renewable tech.",
        "Swarm robotics uses simple rules to create complex group behavior."
    ]
    
    # Insert them
    print("... Injecting Biology Notes")
    for note in biology_notes:
        mem.process_and_store_document(note, source_id="bio_notes.txt")
        
    print("... Injecting Tech Notes")
    for note in tech_notes:
        mem.process_and_store_document(note, source_id="tech_notes.txt")
        
    print("✅ Seeding Complete. The brain now has 10 memories.")

if __name__ == "__main__":
    seed_brain()