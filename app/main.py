from fastapi import FastAPI, Query
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
    return compose_weights(req.problem_type_hash, req.facets or [], req.top_k)
