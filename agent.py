import json
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI

from typing import Literal, Union

from prompt import SYSTEM_PROMPT
from pydantic import BaseModel, TypeAdapter, ValidationError
load_dotenv()


class ContentStep(BaseModel):
    step: Literal["START", "PLAN", "OUTPUT"]
    content: str


class ToolStep(BaseModel):
    step: Literal["TOOL"]
    tool: Literal["get_weather"]
    input: str


AgentStep = Union[ContentStep, ToolStep]
agent_step_adapter = TypeAdapter(AgentStep)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_weather(city: str) -> str:
    url = f"https://wttr.in/{city}?format=%c+%t"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        return f"Error fetching weather: {e}"


def run_agent(query: str, model: str = "gpt-5.5", on_step=None) -> str:
    """Runs the START/PLAN/TOOL/OUTPUT loop for a single query and returns the final answer.

    If given, on_step(step_dict) is called for every PLAN/TOOL/OBSERVE/OUTPUT step,
    so callers (CLI, UI) can surface the agent's reasoning as it happens.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps({"step": "START", "content": query})},
    ]

    while True:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=messages,
        )
        content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": content})

        try:
            parsed = agent_step_adapter.validate_json(content)
        except ValidationError as e:
            observation = {"step": "OBSERVE", "content": f"Error: malformed step from model: {e}"}
            if on_step:
                on_step(observation)
            messages.append({"role": "user", "content": json.dumps(observation)})
            continue

        if on_step:
            on_step(parsed.model_dump())

        if parsed.step == "OUTPUT":
            return parsed.content

        if parsed.step == "TOOL":
            if parsed.tool == "get_weather":
                result = get_weather(parsed.input)
            else:
                result = f"Error: unknown tool '{parsed.tool}'"

            observation = {"step": "OBSERVE", "content": result}
            if on_step:
                on_step(observation)
            messages.append({"role": "user", "content": json.dumps(observation)})
            continue

        # nudge the model to continue — keeps last turn as "user"
        messages.append({"role": "user", "content": json.dumps({"step": "continue"})})
