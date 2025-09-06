import os
import json
import hashlib
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def hash_problem(problem_json):
    """
    Deterministic SHA‑256 hash of the problem spec.
    """
    return hashlib.sha256(
        json.dumps(problem_json, sort_keys=True).encode()
    ).hexdigest()

def ingest(filepath: str):
    """
    Reads a JSON file of challenges, inserts them as CHALLENGE rows.
    """
    with open(filepath) as f:
        challenges = json.load(f)
    for ch in challenges:
        hash_id = hash_problem(ch)
        print(f"Ingesting problem with hash {hash_id}...")
        sb.table("coder_memory").insert({
            "record_type": "CHALLENGE",
            "problem_type_hash": hash_id,
            "generator_spec": ch,
            "facets": ch.get("tags", []),
        }).execute()
    print(f"Ingested {len(challenges)} challenges successfully!")

if __name__ == "__main__":
    ingest("data/opencoder_challenges.json")
