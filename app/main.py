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
@app.post("/feedback/preference")
def record_preference(preferred_id: str = Body(...), other_id: str = Body(...)):
    # Fetch preferred profile
    preferred = sb.table("coder_memory").select("*").eq("id", preferred_id).execute().data
    if not preferred:
        return {"error": "Preferred ID not found"}
    preferred = preferred[0]

    # Update preference score
    metrics = preferred.get("metrics", {})
    new_score = metrics.get("preference_score", 0) + 1
    updated_metrics = {**metrics, "preference_score": new_score}

    sb.table("coder_memory").update({
        "metrics": updated_metrics
    }).match({"id": preferred_id}).execute()

    return {"status": "recorded", "preferred_id": preferred_id}

