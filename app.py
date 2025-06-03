# app.py
from flask import Flask, request, jsonify
import subprocess
import shlex

app = Flask(__name__)

def run_mistral(user_prompt: str) -> str:
    """
    Calls Ollama’s CLI to run the local “mistral” model on user_prompt.
    Returns the generated text as a string, or "" on error.
    """
    cmd = f"ollama run mistral {shlex.quote(user_prompt)}"
    try:
        completed = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=90 # how long a prompt has until it we stop it
        )
        if completed.returncode != 0:
            return ""
        return completed.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""



@app.route("/generate", methods=["POST"])
def generate():
    data        = request.json or {}
    user_prompt = data.get("prompt", "").strip()

    # (1) Directly send every prompt to Mistral, without any jailbreak filtering
    mistral_reply = run_mistral(user_prompt)
    return jsonify({"response": mistral_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
