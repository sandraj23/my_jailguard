# mutators.py

import random

def insert_random_punct(prompt: str) -> str:
    """
    Insert a random punctuation mark somewhere in the prompt (avoiding first/last character).
    """
    if len(prompt) < 4:
        return prompt
    i = random.randint(1, len(prompt) - 2)
    punct = random.choice([".", ",", ";", ":", "-", "?"])
    return prompt[:i] + punct + prompt[i:]


def delete_random_char(prompt: str) -> str:
    """
    Delete a single non‐whitespace character at random.
    """
    indices = [i for i, c in enumerate(prompt) if not c.isspace()]
    if not indices:
        return prompt
    i = random.choice(indices)
    return prompt[:i] + prompt[i+1:]


def swap_adjacent_words(prompt: str) -> str:
    """
    Swap two adjacent words in the prompt at random.
    """
    words = prompt.split()
    if len(words) < 2:
        return prompt
    i = random.randint(0, len(words) - 2)
    words[i], words[i+1] = words[i+1], words[i]
    return " ".join(words)


# A list of all mutators; classify_with_mutations will pick randomly from here
ALL_MUTATORS = [insert_random_punct, delete_random_char, swap_adjacent_words]
