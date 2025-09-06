from supabase import create_client
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

VECTOR_DIM = 384  # match your DB schema

class ComposeRequest(BaseModel):
    problem_type_hash: str
    facets: List[str]
    top_k: int = 3

def compose_weights(request: ComposeRequest):
    response = (
        supabase.table("coder_memory")
        .select("*")
        .eq("record_type", "PROFILE")
        .eq("problem_type_hash", request.problem_type_hash)
        .order("profile_rank", desc=False)
        .limit(request.top_k)
        .execute()
    )

    profiles = response.data

    if not profiles:
        return {"weights": [0.0] * VECTOR_DIM, "source": "empty_fallback"}

    result = [0.0] * VECTOR_DIM
    for profile in profiles:
        delta = profile.get("weights_delta", {})
        for k, v in delta.items():
            result[int(k)] += float(v)

    # Normalize if needed
    normed = [round(x / len(profiles), 6) for x in result]
    return {"weights": normed, "source": "supabase_profiles"}
# =======
from supabase import create_client
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

VECTOR_DIM = 384  # match your DB schema

class ComposeRequest(BaseModel):
    problem_type_hash: str
    facets: List[str]
    top_k: int = 3

def compose_weights(request: ComposeRequest):
    response = (
        supabase.table("coder_memory")
        .select("*")
        .eq("record_type", "PROFILE")
        .eq("problem_type_hash", request.problem_type_hash)
        .order("profile_rank", desc=False)
        .limit(request.top_k)
        .execute()
    )

    profiles = response.data

    if not profiles:
        return {"weights": [0.0] * VECTOR_DIM, "source": "empty_fallback"}

    result = [0.0] * VECTOR_DIM
    for profile in profiles:
        delta = profile.get("weights_delta", {})
        for k, v in delta.items():
            result[int(k)] += float(v)

    # Normalize
    normed = [round(x / len(profiles), 6) for x in result]
    return {"weights": normed, "source": "supabase_profiles"}
# >>>>>>> dd17ab9 (Fix compose_weights argument signature)
