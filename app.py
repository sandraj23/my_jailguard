# app.py
from flask import Flask, request, jsonify
import subprocess
import shlex

app = Flask(__name__)

# # 1) Expand these lists as needed
# MALICIOUS_TOPICS = {
#     "hack",
#     "bank account",
#     "methamphetamine",
#     "bomb",
#     "ransomware",
#     "slur",
#     # …add more “topics” that you consider disallowed
# }

# INTENT_WORDS = {
#     "how to",
#     "teach me",
#     "show me",
#     "step-by-step",
#     "build",
#     "manufacture",
#     "code to",
#     "break into",
#     "say",
#     # …you can add other indicator phrases
# }

# def contains_forbidden(text: str) -> bool:
#     """
#     Return True only if the prompt mentions a MALICIOUS_TOPIC
#     AND also contains an INTENT_WORD (i.e. asking for instructions).
#     """
#     low = text.lower()
#     topic_found = any(topic in low for topic in MALICIOUS_TOPICS)
#     intent_found = any(intent in low for intent in INTENT_WORDS)
#     return topic_found and intent_found

def run_mistral(user_prompt: str, timeout: int = 90) -> str:
    cmd = f"ollama run mistral {shlex.quote(user_prompt)}"
    try:
        completed = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if completed.returncode != 0:
            return ""
        return completed.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""

def is_malicious_via_model(text: str) -> bool:
    """
    Ask Mistral to classify whether a given prompt is malicious.
    """
    classification_prompt = (
        "Answer with 'Yes' or 'No' only. "
        "Is the following request asking for illegal, harmful, or malicious instructions? "
        f"\"{text}\""
    )
    response = run_mistral(classification_prompt, timeout=30).lower()
    return "yes" in response.split()

@app.route("/generate", methods=["POST"])
def generate():
    data        = request.json or {}
    user_prompt = data.get("prompt", "").strip()

    # # 2a) Heuristic refusal: topic + intent
    # if contains_forbidden(user_prompt):
    #     return jsonify({"response": "I’m sorry, I can’t comply with that."})

    # 2b) Model-based refusal: ask Mistral if it's malicious
    try:
        if is_malicious_via_model(user_prompt):
            return jsonify({"response": "I’m sorry, I can’t comply with that."})
    except Exception:
        # If classification call fails, fall back to heuristic only
        pass

    # 3) Otherwise, call Mistral
    mistral_reply = run_mistral(user_prompt)
    return jsonify({"response": mistral_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
