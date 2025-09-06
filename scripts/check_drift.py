def detect_low_pass_profiles(threshold=0.2):
    rows = sb.table("coder_memory").select("*").eq("record_type", "PROFILE").execute().data
    flagged = [r for r in rows if r.get("metrics", {}).get("pass_rate", 1) < threshold]
    print(f"Found {len(flagged)} low-pass profiles.")
    return flagged
