from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Optional
from app.weights import compose_weights
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment + connect Supabase
load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# FastAPI app
app = FastAPI()

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}
    
@app.get("/debug/embeddings")
def dump_embeddings():
    profiles = (
        sb.table("coder_memory")
        .select("id, profile_rank, facets, weights_delta")
        .eq("record_type", "PROFILE")
        .execute()
        .data
    )

    def to_vector(d):
        vec = [0.0] * 384
        for k, v in d.items():
            vec[int(k)] = float(v)
        return vec

    return [
        {
            "id": p["id"],
            "facets": p["facets"],
            "profile_rank": p["profile_rank"],
            "vector": to_vector(p["weights_delta"]),
        }
        for p in profiles if p.get("weights_delta")
    ]


# === Compose Weights ===
class ComposeRequest(BaseModel):
    problem_type_hash: str
    facets: Optional[List[str]] = None
    top_k: int = 5

@app.post("/compose_weights")
def compose_route(req: ComposeRequest):
    return compose_weights(req)

# === Feedback API ===
from datetime import datetime

@app.post("/feedback/preference")
def record_preference(preferred_id: str = Body(...), other_id: str = Body(...)):
    # Fetch preferred profile to validate it exists
    preferred = sb.table("coder_memory").select("*").eq("id", preferred_id).execute().data
    if not preferred:
        return {"error": "Preferred ID not found"}
    
    # Log feedback
    sb.table("feedback").insert({
        "preferred_id": preferred_id,
        "other_id": other_id,
        "timestamp": datetime.utcnow().isoformat()
    }).execute()

    return {
        "status": "recorded",
        "preferred_id": preferred_id
    }
from fastapi import Body
from datetime import datetime
from uuid import uuid4

@app.post("/challenge/results")
def post_challenge_results(
    challenge_id: str = Body(...),
    prompt: str = Body(...),
    solution: str = Body(...),
    result: dict = Body(...),
    profile_snapshot: dict = Body(None)
):
    # Construct the record to store in `coder_memory` as a new row
    new_id = str(uuid4())
    timestamp = datetime.utcnow().isoformat()

    record = {
        "id": new_id,
        "ts": timestamp,
        "record_type": "CHALLENGE",
        "challenge_id": challenge_id,
        "prompt": prompt,
        "solution": solution,
        "result": result,
        "profile_snapshot": profile_snapshot,
    }

    sb.table("coder_memory").insert(record).execute()

    return {
        "status": "recorded",
        "challenge_id": challenge_id,
        "record_id": new_id
    }



