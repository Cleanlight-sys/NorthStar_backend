import json
import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Load or import your schema, e.g., from schema/profile.json
from schema.profile import PROFILE_SCHEMA  # stub or actual file

SAMPLE_PROFILE_ROW = {
    "id": "c59d2290-7c21-4f76-b425-412a113f9872",
    "ts": "2025-09-06T17:47:05.368732+00:00",
    "record_type": "PROFILE",
    "problem_type_hash": "abc123",
    "facets": ["fac1", "fac2"],
    "embedding": "[0.1,0.1, ... 384 dims]",
    "weights_base_ref": None,
    "weights_delta": {"0": 0.01, "1": 0.02, "2": 0.03},
    "profile_rank": 1,
    "centroid_flag": True,
    "metrics": {"pass_rate": 0},
    "artifact_refs": {},
    "generator_spec": None,
    "validators_spec": None,
    "notes": "Test 384-dim profile"
}

def test_profile_schema_valid():
    try:
        validate(instance=SAMPLE_PROFILE_ROW, schema=PROFILE_SCHEMA)
    except ValidationError as e:
        pytest.fail(f"Profile row schema invalid: {e.message}")
