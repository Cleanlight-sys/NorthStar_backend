import argparse
from datasets import load_dataset
import random

def run_manual_challenge(dataset_name: str, index: int = None):
    ds = load_dataset(dataset_name, split="train")
    
    if index is None:
        index = random.randint(0, len(ds) - 1)

    challenge = ds[index]
    prompt = challenge.get("question") or challenge.get("prompt") or "[No prompt]"
    response = challenge.get("answer") or challenge.get("completion") or "[No answer]"

    print(f"Dataset: {dataset_name}")
    print(f"Index: {index}")
    print("Prompt:\n", prompt)
    print("Response:\n", response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="glaiveai/glaive-code-assistant")
    parser.add_argument("--index", type=int, default=None)
    args = parser.parse_args()

    run_manual_challenge(args.dataset, args.index)
