# test_classify.py

import csv
from app import classify_prompt

if __name__ == "__main__":
    # Load prompts and labels from text.csv
    examples = []  # List of (prompt, label)
    with open("large_test_prompts.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prompt = row.get("prompt", "").strip()
            label_str = row.get("label", "").strip()
            if prompt and label_str in ("0", "1"):
                examples.append((prompt, int(label_str)))

    if not examples:
        print("No valid (prompt,label) pairs found in text.csv.")
        exit(1)

    # Initialize counts
    tp = tn = fp = fn = 0

    # Evaluate each example
    for idx, (prompt, label) in enumerate(examples, start=1):
        is_malicious = classify_prompt(prompt)  # True = model said "YES"
        # If label == 1, it’s actually malicious and should be refused (is_malicious=True).
        # If label == 0, it’s benign and should be allowed (is_malicious=False).
        if label == 1 and is_malicious:
            tp += 1
        elif label == 1 and not is_malicious:
            fn += 1
        elif label == 0 and not is_malicious:
            tn += 1
        elif label == 0 and is_malicious:
            fp += 1

        print(f"[{idx}/{len(examples)}] Prompt: {prompt!r} | "
              f"Label={label} | Classified={'Malicious' if is_malicious else 'Benign'}")

    # Compute metrics
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0

    # Print confusion matrix and metrics
    print("\n=== Confusion Matrix ===")
    print(f" True Positives  (malicious refused):   {tp}")
    print(f" False Positives (benign refused):      {fp}")
    print(f" False Negatives (malicious allowed):   {fn}")
    print(f" True Negatives  (benign allowed):      {tn}")
    print()
    print(f"Accuracy:  {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
