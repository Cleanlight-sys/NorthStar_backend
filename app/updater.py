from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
ALPHA = 0.1  # EMA smoothing factor

def update_profile_delta(profile_id: str, new_delta: dict):
    """
    Blend new run deltas into an existing profile using EMA logic.
    """
    # Fetch current row
    prev = sb.table("coder_memory").select("*").eq("id", profile_id).single().execute().data

    if not prev or prev["record_type"] != "PROFILE":
        raise ValueError("Invalid profile row")

    current_delta = prev.get("weights_delta", {})

    # EMA blend
    updated = {}
    for k in set(current_delta.keys()).union(new_delta.keys()):
        old_val = float(current_delta.get(k, 0.0))
        new_val = float(new_delta.get(k, 0.0))
        updated[k] = round(ALPHA * new_val + (1 - ALPHA) * old_val, 6)

    # Update in Supabase
    sb.table("coder_memory").update({
        "weights_delta": updated,
        "ts": "now()"  # optional: timestamp bump
    }).match({"id": profile_id}).execute()

    return {"status": "updated", "profile_id": profile_id}
