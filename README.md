# Assignment 1 — Student Support Agent

This repository contains the Assignment 1 implementation of a student-support agent. It uses Groq as the only LLM provider and implements local tool calling, local policy retrieval, explicitly scoped non-sensitive memory, and privacy-aware operational tracing.

No real student information, API keys, or fabricated demonstration records are stored in this repository.

## Prerequisites

- Python 3.10 or newer
- A Groq API key from [Groq Console](https://console.groq.com/keys)
- VS Code with the Python extension recommended

## Setup in VS Code

Open the `Assignment_1_Student_Support_Agent` folder in VS Code, then open its integrated terminal and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
Copy-Item .env.example .env
```

If `py -3.11` is unavailable, use the version installed on your computer, for example `py -3.12`. If the `py` command is unavailable, install Python 3.10+ from [python.org](https://www.python.org/downloads/windows/) and select **Add Python to PATH** during installation.

Open `.env` and replace only the placeholder value after `GROQ_API_KEY=` with your Groq key. Keep `.env` private: it is excluded by `.gitignore`.

## Verify Groq Connection

With the virtual environment activated, run:

```powershell
python -m student_support_agent --check-groq
```

The command makes an authenticated request to Groq's models endpoint and prints the number of models returned. It never prints your API key and does not send a chat completion.

## Run Tests

```powershell
pytest
```

The included tests run without a Groq key or network connection.

## Evaluate the Agent

Copy `data/evaluation/cases.template.json` to `data/evaluation/cases.json`, then add your reviewed, non-sensitive cases using this structure:

```json
[
  {
    "id": "unique-case-id",
    "message": "A non-sensitive test question",
    "expected_terms": ["required wording"],
    "required_tools": ["search_policy"]
  }
]
```

Run the reviewed cases with:

```powershell
python -m student_support_agent --evaluate
```

The resulting local report records task success, required-tool use, latency, and Groq token usage where available. It intentionally excludes the evaluated messages and answers.

## Included Evidence

`evidence/assignment1_evaluation_summary.json` is a reviewed, sanitized summary of five fictional policy cases. It records a 100% task-success rate, per-case tool use, latency, and Groq token usage without including prompts, answers, credentials, or student data.

## Ask the Agent

Add approved, non-sensitive policy documents as `.md` or `.txt` files to `data/policies/`. The agent deliberately does not invent institutional policies when that folder has no matching source material.

Run one request with:

```powershell
python -m student_support_agent --ask "Your question here"
```

The agent prints a response and operational metrics. It writes local preference memory and privacy-aware trace records to `data/runtime/`, which is excluded from Git. Trace records contain timing, token counts when Groq provides them, tool names, and status; they do not store prompts, responses, API keys, or student data.

## Streamlit Interface

After installing requirements, run the local interface with:

```powershell
python -m streamlit run streamlit_app.py
```

The terminal will show the local browser address. The interface reuses the same agent, tools, policy retrieval, memory, and tracing code as the command-line command. It displays only the response, safe runtime metrics, and tool status; it never displays the API key.

## Current Structure

```text
src/student_support_agent/
  agent.py               # Bounded Groq tool-calling loop
  config.py              # Reads and validates private configuration
  groq_connection.py     # Isolated Groq connectivity check
  memory.py              # Persistent allow-listed non-sensitive preferences
  retrieval.py           # Bounded local policy-context selection
  tools.py               # Tool schemas and application-side execution
  tracing.py             # Privacy-aware operational records
  evaluation.py          # Reviewed-case evaluation and sanitized reports
  __main__.py            # Command-line entry point
tests/                   # Offline unit tests
data/                    # Reserved for later project-owned data
```

## Security Rules

- Never add API keys, passwords, tokens, or student data to Git.
- Keep `.env` local and create a new Groq key if one is exposed.
- Use only the Groq Python SDK for language-model calls in this project.

## Roadmap

The next phases add evaluation cases and submission evidence. Assignment 2 will extend this project in a separate folder with identity, authorization, approvals, and audit records.

