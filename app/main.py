from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import os
import random

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

app = FastAPI()

# Models
class ChallengeResult(BaseModel):
    challenge_id: str
    prompt: str
    solution: str
    result: Dict[str, Optional[str]]
    profile_snapshot: Optional[dict] = None

# Routes
@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/challenge/next")
def get_next_challenge():
    challenges = sb.table("coder_memory").select("*").eq("record_type", "CHALLENGE").execute().data
    if not challenges:
        return {"error": "No challenges found"}
    sample = random.choice(challenges)
    return {
        "id": sample["id"],
        "prompt": sample.get("prompt") or sample.get("generator_spec", {}).get("prompt")
    }

@app.get("/challenge/answer")
def get_challenge_answer(id: str = Query(...)):
    row = sb.table("coder_memory").select("*").eq("id", id).single().execute().data
    if not row:
        return {"error": "Challenge not found"}
    return {"answer": row.get("answer") or row.get("generator_spec", {}).get("answer")}

@app.post("/challenge/submit")
def post_challenge_results(payload: ChallengeResult):
    record = {
        "id": f"run_{datetime.utcnow().isoformat()}",
        "ts": datetime.utcnow().isoformat(),
        "record_type": "RUN",
        **payload.dict()
    }
    sb.table("coder_memory").insert(record).execute()
    return {"status": "recorded", "challenge_id": payload.challenge_id}

@app.get("/challenge/results")
def get_challenge_results(
    sort_by: Optional[str] = Query(None),
    limit: Optional[int] = Query(50),
    profile_id: Optional[str] = Query(None)
):
    q = sb.table("coder_memory").select("*").eq("record_type", "RUN")
    if profile_id:
        q = q.eq("profile_snapshot->>id", profile_id)
    if sort_by:
        q = q.order(sort_by, desc=True)
    if limit:
        q = q.limit(limit)
    return q.execute().data
