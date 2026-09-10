# Weather Agent

An AI-powered Weather Agent built with OpenAI and Streamlit that plans its steps, fetches live weather data, and responds in a natural, human-friendly way.

## Overview

This project is a simple agentic AI app focused on weather queries. Instead of directly returning a hardcoded response, the assistant follows a small reasoning loop:

`START -> PLAN -> TOOL -> OBSERVE -> OUTPUT`

The model first decides what it needs to do, calls a weather tool when required, observes the result, and then generates a final answer. The app includes a clean Streamlit UI where you can enter a city and watch the agent work step by step.

## Features

- Agent-style reasoning flow with structured steps
- Live weather lookup using `wttr.in`
- Streamlit UI for interactive use
- Step-by-step reasoning display
- CLI entrypoint for quick terminal testing
- India-focused weather responses

## Tech Stack

- Python
- OpenAI API
- Streamlit
- Requests
- Pydantic
- `wttr.in`

## Project Structure

```text
.
├── app.py              # Streamlit frontend
├── agent.py            # Agent loop and tool execution
├── weather_agent.py    # CLI entrypoint
├── prompt.py           # System prompt and agent rules
└── requirements.txt    # Python dependencies
```

## How It Works

1. The user asks for the weather in a city.
2. The model returns a `PLAN` step describing what it will do.
3. The agent triggers the `get_weather` tool.
4. The weather result is returned as an `OBSERVE` step.
5. The model produces the final `OUTPUT` in natural language.

This makes the project more than a basic chatbot. It is a small tool-using AI agent with an explicit reasoning-and-action loop.

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Weather-Agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

## Run the App

Start the Streamlit UI:

```bash
streamlit run app.py
```

Then open the local URL shown in your terminal.

## Run in the Terminal

You can also test the agent from the command line:

```bash
python weather_agent.py
```

## Example Query

```text
What is the weather in Mumbai?
```

Example flow:

```text
START -> PLAN -> TOOL(get_weather) -> OBSERVE -> OUTPUT
```

## Why This Is Agentic

This project uses an agent-style workflow because the model:

- plans before answering
- decides when to use a tool
- observes tool results
- produces the final response after reasoning through the task

It is a simple single-tool agent, but it still demonstrates the core idea behind agentic AI.

