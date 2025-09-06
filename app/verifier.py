import subprocess
import tempfile
import os

def verify_run(code: str, tests: str, timeout: int = 5):
    """
    Run the submitted `code` against `tests` in a temp sandbox using pytest.
    """
    with tempfile.TemporaryDirectory() as tmp:
        code_path = os.path.join(tmp, "submission.py")
        test_path = os.path.join(tmp, "test_submission.py")

        with open(code_path, "w") as f:
            f.write(code)

        with open(test_path, "w") as f:
            f.write(tests)

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_path],
                capture_output=True,
                timeout=timeout
            )
            return {
                "passed": result.returncode == 0,
                "stdout": result.stdout.decode(),
                "stderr": result.stderr.decode(),
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Execution timed out after {} seconds".format(timeout)
            }
