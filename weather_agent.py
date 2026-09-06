import json
from .prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
import os
from openai import OpenAI
import requests

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("GEMINI_API_BASE_URL")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

def get_weather(city):
    url = f"https://wttr.in/{city}?format=%c+%t"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        return f"Error fetching weather: {e}"


messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": json.dumps({"step": "START", "content": "Can you tell me the weather of Pune?"})},
]

while True:
    response = client.chat.completions.create(
        model="gemini-3.6-flash",
        response_format={"type": "json_object"},
        messages=messages
    )
    content = response.choices[0].message.content
    parsed = json.loads(content)
    print(parsed)

    messages.append({"role": "assistant", "content": content})

    if parsed["step"] == "OUTPUT":
        break

    # nudge the model to continue — keeps last turn as "user"
    messages.append({"role": "user", "content": json.dumps({"step": "continue"})})