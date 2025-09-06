from supabase.client import supabase
import numpy as np

def compose_weights(problem_type_hash: str, facets: list, top_k: int = 5):
    response = supabase.table("coder_memory") \
        .select("weights_delta") \
        .eq("record_type", "PROFILE") \
        .eq("problem_type_hash", problem_type_hash) \
        .order("profile_rank", desc=False) \
        .limit(top_k) \
        .execute()

    deltas = []
    for row in response.data:
        delta = row["weights_delta"]
        if delta:
            deltas.append(np.array([delta[str(i)] for i in range(60)]))

    if not deltas:
        return {"weights": [0.0] * 60, "source": "empty_top_k"}

    mean_weights = np.mean(deltas, axis=0)
    return {"weights": mean_weights.tolist(), "source": f"top_{top_k}_blend"}
