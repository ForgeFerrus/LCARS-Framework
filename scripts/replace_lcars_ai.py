import re
import os

FILE = "lcars_ai.py"

def redact(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            s = f.read()
    except FileNotFoundError:
        return

    # redact OpenAI keys (sk-...)
    s = re.sub(r"sk-[A-Za-z0-9_\-]{20,}", "OPENAI_REDACTED", s)
    # redact Hugging Face tokens (hf_...)
    s = re.sub(r"hf_[A-Za-z0-9_\-]{20,}", "HF_REDACTED", s)

    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


if __name__ == "__main__":
    redact(FILE)
