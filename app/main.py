from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from typing import List, Optional
from app.weights import compose_weights

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

class ComposeRequest(BaseModel):
    problem_type_hash: str
    facets: Optional[List[str]] = None
    top_k: int = 5

@app.post("/feedback/preference")
def record_preference(preferred_id: str = Body(...), other_id: str = Body(...)):
    # Simple ranking bump
    preferred = sb.table("coder_memory").select("*").eq("id", preferred_id).execute().data[0]
    other = sb.table("coder_memory").select("*").eq("id", other_id).execute().data[0]

    # Increase preference score
    new_score = preferred["metrics"].get("preference_score", 0) + 1
    sb.table("coder_memory").update({
        "metrics": {**preferred["metrics"], "preference_score": new_score}
    }).match({"id": preferred_id}).execute()

    return {"status": "recorded", "preferred_id": preferred_id}
    
@app.post("/compose_weights")
def compose_route(req: ComposeRequest):
    return compose_weights(req.problem_type_hash, req.facets or [], req.top_k)

# =======
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from app.weights import compose_weights

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

class ComposeRequest(BaseModel):
    problem_type_hash: str
    facets: Optional[List[str]] = None
    top_k: int = 5

@app.post("/compose_weights")
def compose_route(req: ComposeRequest):
    return compose_weights(req)  # ✅ Just pass the object

# >>>>>>> dd17ab9 (Fix compose_weights argument signature)
