from app.verifier import verify_run
from app.weights import compose_weights, ComposeRequest
from app.memory import extract_facet_graph, pick_next_challenge
from supabase import create_client
from dotenv import load_dotenv
import os
import random
import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_solution(prompt: str) -> str:
    resp = client.completions.create(
        engine="gpt-4",       # or whichever model you're using
        prompt=prompt,
        max_tokens=256,
        temperature=0.2,
        stop=None
    )
    return resp.choices[0].text
    
load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def run_one_step():
    print("Starting self-train step...")

    # Fetch challenge + profile data
    challenges = sb.table("coder_memory").select("*").eq("record_type", "CHALLENGE").execute().data
    profiles = sb.table("coder_memory").select("*").eq("record_type", "PROFILE").execute().data
    run_history = sb.table("run_history").select("*").order("ts", desc=True).limit(100).execute().data

    if not challenges or not profiles:
        print("Missing challenges or profiles.")
        return

    # Compose weights from top-ranked profiles
    request = ComposeRequest(
        problem_type_hash=challenges[0]["problem_type_hash"],
        facets=[],
        top_k=3
    )
    weights_out = compose_weights(request)

    # Pick next challenge intelligently
    graph = extract_facet_graph(challenges)
    chosen = pick_next_challenge(graph, weights_out, challenges, run_history)[0]

    prompt = chosen["generator_spec"]["prompt"]
    test_code = chosen["generator_spec"]["test"]

    # TODO: Replace with model-generated code
    solution = "# placeholder: solution for prompt\npass"

    # Run verifier
    result = verify_run(solution, test_code)
    print("Test result:", result)

    # Log run
    sb.table("run_history").insert({
        "challenge_id": chosen["problem_type_hash"],
        "profile_id": profiles[0]["id"],
        "ts": str(datetime.datetime.utcnow()),
        "result": result
    }).execute()

if __name__ == "__main__":
    run_one_step()
