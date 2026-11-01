import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load .env from the backend folder
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("HUGGINGFACE_API_KEY")

if not api_key:
    print("ERROR: Hugging Face API key not found!")
    sys.exit(1)

url = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": "google/gemma-2-2b-it",
    "messages": [
        {
            "role": "user",
            "content": "Hello! Introduce yourself in two short sentences."
        }
    ],
    "max_tokens": 100,
    "stream": False,
}

print("API key loaded successfully!")
print("Testing Hugging Face model...")

try:
    response = httpx.post(
        url,
        headers=headers,
        json=payload,
        timeout=90.0
    )

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        result = response.json()

        print("\nAI Response:")
        print(result["choices"][0]["message"]["content"])

    else:
        print("\nAPI Error:")
        print(response.text)

except httpx.RequestError as error:
    print("\nConnection Error:")
    print(error)