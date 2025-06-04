import pickle
import time
import random
from app import classify_with_mutations

if __name__ == "__main__":
    # 1) Load all prompts/metadata
    with open("dataset/text/dataset.pkl",  "rb") as f:
        all_prompts = pickle.load(f)
    with open("dataset/text/dataset-key.pkl", "rb") as f:
        all_metadata = pickle.load(f)

    assert len(all_prompts) == len(all_metadata)

    # 2) Build a list of (idx, prompt, label) for only string‐typed prompts
    examples = []
    for idx, (prompt, meta) in enumerate(zip(all_prompts, all_metadata)):
        if isinstance(prompt, str):
            label = 1 if meta[0].lower() == "jailbroken" else 0
            examples.append((idx, prompt, label))

    print(f"Total string prompts available: {len(examples)}")

    # 3) Randomly sample 500 of those examples
    sample_size = 500
    sampled = random.sample(examples, k=sample_size)

    tp = tn = fp = fn = 0
    start_time = time.time()

    # 4) Evaluate only the 500 sampled prompts
    for count, (_, prompt, label) in enumerate(sampled, start=1):
        is_malicious = classify_with_mutations(prompt, num_variants=2)

        if label == 1 and is_malicious:
            tp += 1
        elif label == 1 and not is_malicious:
            fn += 1
        elif label == 0 and not is_malicious:
            tn += 1
        elif label == 0 and is_malicious:
            fp += 1

        if count % 100 == 0 or count == sample_size:
            elapsed = time.time() - start_time
            print(f"[{count}/{sample_size}] TP={tp}  FP={fp}  FN={fn}  TN={tn}  elapsed={elapsed:.1f}s")

    # 5) Compute metrics over the 500
    accuracy  = (tp + tn) / sample_size
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall    = tp / (tp + fn) if (tp + fn) else 0

    print("\n=== Phase 1 Results on 500‐Prompt Sample ===")
    print(f" True Positives:   {tp}")
    print(f" False Positives:  {fp}")
    print(f" False Negatives:  {fn}")
    print(f" True Negatives:   {tn}\n")
    print(f"Accuracy:  {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
