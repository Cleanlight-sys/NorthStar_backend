from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
from datasets import load_dataset
from itertools import islice
import os
import random

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

app = FastAPI()

class ChallengeResult(BaseModel):
    challenge_id: str
    prompt: str
    solution: str
    result: Dict[str, Optional[str]]
    profile_snapshot: Optional[dict] = None

@app.get("/health")
def get_health():
    return {"status": "ok"}

from datasets import load_dataset
from itertools import islice

@app.get("/challenge/next")
def get_next_challenge():
    ds = load_dataset("glaiveai/glaive-code-assistant", split="train", streaming=True)
    index = random.randint(0, 100_000)
    sample = next(islice(ds, index, None))
    return {
        "id": f"glaive-{index}",
        "prompt": sample["question"]
    }
    
@app.get("/challenge/answer")
def get_challenge_answer(id: str = Query(...)):
    index = int(id.replace("glaive-", ""))
    ds = load_dataset("glaiveai/glaive-code-assistant", split="train", streaming=True)
    sample = next(islice(ds, index, None))
    return {"answer": sample["answer"]}
    
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

