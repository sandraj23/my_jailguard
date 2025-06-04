# test_injections.py
import requests

BASE_URL = "http://localhost:5000"

def test_injections():
    with open("mixed.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for idx, injection in enumerate(lines, start=1):
        payload = {"prompt": injection}
        try:
            r = requests.post(f"{BASE_URL}/generate", json=payload, timeout=30)
            response_text = r.json().get("response", "No response key")
        except Exception as e:
            response_text = f"ERROR: {e}"

        print(f"--- Injection #{idx} ---")
        print(injection)
        print("→ LLM Response:")
        print(response_text)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_injections()
