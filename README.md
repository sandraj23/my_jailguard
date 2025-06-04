# JailGuardLite

A lightweight, mutation‐based prompt‐injection detection demo using GPT-3.5-turbo.  
This repository implements a simplified version of the JailGuard approach: for each incoming prompt, it applies two random text mutations and checks whether any variant causes GPT to refuse. If so, the original prompt is flagged as malicious; otherwise, it is allowed.

---

## Repository Contents

- **`app.py`**  
  - A Flask app that exposes a single `/generate` endpoint.  
  - It runs a zero-shot “YES/NO” classifier via GPT-3.5-turbo on the original prompt.  
  - If the original is not refused, it applies two random mutators (in `mutators.py`), re-classifies each variant, and refuses if any variant is flagged.

- **`mutators.py`**  
  - Defines three simple text-mode mutators:  
    1. `insert_random_punct(prompt)`: insert a random punctuation character at a random non-space position.  
    2. `delete_random_char(prompt)`: delete a random non-whitespace character.  
    3. `swap_adjacent_words(prompt)`: swap one randomly chosen pair of adjacent words.  
  - The Flask app uses these to generate two mutated variants per prompt.

- **`evaluate_phase1.py`**  
  - Loads JailGuard’s full text dataset (`dataset/text/dataset.pkl` and `dataset/text/dataset-key.pkl`).  
  - Filters to plain-string prompts, applies the two-mutation logic from `app.py` to each, and tallies true positives, false positives, false negatives, and true negatives.  
  - Prints overall accuracy, precision, and recall on the entire dataset.

---

## Prerequisites

1. **Python 3.8+**  
2. **An OpenAI API key** (GPT-3.5-turbo must be enabled on your account).  
3. The JailGuard text dataset (pickles):
   - `dataset/text/dataset.pkl`  
   - `dataset/text/dataset-key.pkl`  

---

## Installation & Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/sandraj23/my_jailguard.git
   cd jailguardlite

2. **Create a virtual environment**
    python -m venv venv
    # macOS/Linux:
    source venv/bin/activate
    # Windows:
    venv\Scripts\activate.bat

3. **Install dependencies**
    pip install flask openai python-dotenv

4. **Obtain an OpenAI API key**
    Sign up at https://platform.openai.com if you haven’t already.
    Create an API key (Settings → API Keys → Create new secret key).

5. **Create a .env file in the project root with the following content:**
    OPENAI_API_KEY=sk-your_openai_api_key_here

## Running the Flask App

1. **Ensure your venv is activated and .env is set.**
    python app.py

## Evaluating on the Full Dataset/Sample
1. **Start the Flask server (as above).**

2. **In a separate terminal (venv still activated), run:**
    python evaluate_phase1.py

3. **Output**
    Progress prints every 500 evaluated prompts (skipping non-string entries).
    Final confusion matrix and metrics (accuracy, precision, recall) on all string-typed prompts in the JailGuard dataset.

