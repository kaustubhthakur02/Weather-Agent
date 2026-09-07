import json
from prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
import os
from openai import OpenAI
import requests

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(
    api_key=api_key,
)

def get_weather(city):
    url = f"https://wttr.in/{city}?format=%c+%t"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        return f"Error fetching weather: {e}"
    



input_query = input("Enter your weather query: ")

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": json.dumps({"step": "START", "content": input_query})},
]

while True:
    response = client.chat.completions.create(
        model="gpt-5.5",
        response_format={"type": "json_object"},
        messages=messages
    )
    content = response.choices[0].message.content
    parsed = json.loads(content)
    print(parsed)

    messages.append({"role": "assistant", "content": content})

    if parsed["step"] == "OUTPUT":
        break

    if parsed["step"] == "TOOL":
        tool_name = parsed.get("tool")
        tool_input = parsed.get("input")

        if tool_name == "get_weather":
            result = get_weather(tool_input)
        else:
            result = f"Error: unknown tool '{tool_name}'"

        messages.append({"role": "user", "content": json.dumps({"step": "OBSERVE", "content": result})})
        continue

    # nudge the model to continue — keeps last turn as "user"
    messages.append({"role": "user", "content": json.dumps({"step": "continue"})})