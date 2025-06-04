# app.py

import os
import random
from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv

from mutators import ALL_MUTATORS

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)


#  CONFIGURATION (token estimates are just for reference; no in‐code budgeting)
#  Below variables were used for reference when considering token cost with the OpenAI API.
#  These are NOT used within the code. 

EST_CLASSIFY_INPUT_TOKS   = 20   # ~20 tokens for the “YES/NO” classifier prompt
EST_CLASSIFY_OUTPUT_TOKS  = 1    # model outputs 1 token: “YES” or “NO”
EST_ANSWER_INPUT_TOKS     = 20   # ~20 tokens in for a normal answer
EST_ANSWER_OUTPUT_TOKS    = 100  # ~100 tokens out for a typical answer


#  CORE FUNCTIONS

def classify_prompt(prompt: str) -> bool:
    """
    Stage 1: Zero‐shot “YES/NO” classification via GPT-3.5-turbo.
    Return True  if the model says “YES” (malicious).
    Return False if it says “NO” (benign).
    """
    short_meta = (
        "You are a security classifier. "
        "If the user’s request is for illegal, harmful, or malicious instructions, "
        'respond with EXACTLY "YES" and stop. '
        'Otherwise respond with EXACTLY "NO".\n\n'
        f'Request: "{prompt}"\n'
        "Answer:"
    )

    resp = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a security classifier."},
            {"role": "user",   "content": short_meta}
        ],
        max_tokens=EST_CLASSIFY_OUTPUT_TOKS,
        temperature=0.0,
        n=1
    )
    raw = resp.choices[0].message.content.strip().upper().rstrip(".")
    print(f"[CLASSIFY] prompt={prompt!r} → raw verdict={repr(raw)}")
    return (raw == "YES")


def answer_prompt(prompt: str) -> str:
    """
    Stage 2: Use GPT-3.5-turbo to answer the benign prompt.
    """
    full_meta = f"Answer the following question concisely:\n\n{prompt}"
    resp = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": full_meta}
        ],
        max_tokens=EST_ANSWER_OUTPUT_TOKS,
        temperature=0.0,
        n=1
    )
    answer = resp.choices[0].message.content.strip()
    print(f"[ANSWER] prompt={prompt!r} → answer starts={repr(answer[:50])}…")
    return answer


#  Phase 1: Binary‐Flip JailGuard

def classify_with_mutations(prompt: str, num_variants: int = 2) -> bool:
    """
    1) Classify the original prompt with classify_prompt().
       - If it’s malicious (“YES”), return True immediately.
    2) Otherwise, generate `num_variants` random mutations.
       - If any mutated prompt is classified as malicious, return True.
    3) If none are malicious, return False (benign).
    """
    # Stage 1: original
    if classify_prompt(prompt):
        return True

    # Stage 2: apply mutators
    chosen = random.sample(ALL_MUTATORS, k=min(num_variants, len(ALL_MUTATORS)))
    for m in chosen:
        mutated = m(prompt)
        print(f"[MUTATOR] applied {m.__name__} → {mutated!r}")
        if classify_prompt(mutated):
            print(f"[MUTATION DETECTED] {mutated!r} flagged as malicious")
            return True

    # No mutation flagged as malicious
    return False



#  Flask Route


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    user_prompt = (data.get("prompt") or "").strip()
    if not user_prompt:
        return jsonify({"response": "I’m sorry, I can’t comply with that."})

    # Use the binary‐flip classifier
    is_bad = classify_with_mutations(user_prompt, num_variants=2)

    if is_bad:
        return jsonify({"response": "I’m sorry, I can’t comply with that."})

    # If still benign, answer normally
    answer = answer_prompt(user_prompt)
    return jsonify({"response": answer})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
