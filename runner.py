"""Runner — takes the user's prompt + a sample input, calls OpenRouter, returns the model output."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Use a capable but cost-effective model as the "student model"
STUDENT_MODEL = "openai/gpt-4o-mini"


def run_prompt(user_prompt: str, sample_input: str) -> str:
    """
    Takes the user's prompt and the level's sample input.
    Constructs a message where the user_prompt is the system instruction
    and the sample_input is the user message. Returns the model's text response.
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key-here":
        return "ERROR: OPENROUTER_API_KEY not set. Please add your key to the .env file."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    # If the user prompt contains {input}, substitute it. Otherwise append it.
    if "{input}" in user_prompt:
        filled_prompt = user_prompt.replace("{input}", sample_input)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": filled_prompt},
        ]
    else:
        messages = [
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": sample_input},
        ]

    payload = {
        "model": STUDENT_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"ERROR: API call failed — {str(e)}"
    except (KeyError, IndexError, ValueError) as e:
        return f"ERROR: Unexpected API response — {str(e)}"