
import os
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("HUGGINGFACE_API_KEY")

if not api_key:
    print("ERROR: Hugging Face API key not found!")
    raise SystemExit(1)

url = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": "Qwen/Qwen2.5-3B-Instruct",
    "messages": [
        {
            "role": "user",
            "content": "Hello! Introduce yourself in two sentences."
        }
    ],
    "max_tokens": 100,
    "stream": False,
}

try:
    response = httpx.post(
        url,
        headers=headers,
        json=payload,
        timeout=90,
    )

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        result = response.json()
        print("\nQwen Response:")
        print(result["choices"][0]["message"]["content"])
    else:
        print("\nAPI Error:")
        print(response.text)

except httpx.RequestError as error:
    print("Connection Error:", error)
