from fastapi import FastAPI
from app.weights import compose_weights, ComposeRequest
from app.verifier import verify_run
from app.updater import update_profile_delta
from supabase import create_client
import os

app = FastAPI()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

@app.post("/submit")
def run_and_update(req: ComposeRequest, code: str):
    # 1. Blend weights
    weights_out = compose_weights(req)
    
    # 2. Pick top challenge (stub)
    challenge = (
        sb.table("coder_memory")
        .select("*")
        .eq("record_type", "CHALLENGE")
        .eq("problem_type_hash", req.problem_type_hash)
        .limit(1).execute().data[0]
    )

    # 3. Run verifier
    result = verify_run(code, tests=challenge["generator_spec"]["test"])

    # 4. Compute new delta (stub)
    new_delta = {"0": 0.1, "3": -0.2}  # TODO: real logic
    profile_id = "c59d2290..."         # TODO: select best profile match

    update_profile_delta(profile_id, new_delta)

    return {
        "challenge_id": challenge["id"],
        "verifier_result": result,
        "updated_profile": profile_id,
        "source": weights_out["source"]
    }
