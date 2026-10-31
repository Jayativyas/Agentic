"""Flask interface for the Assignment 1 Student Support Agent."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from student_support_agent.agent import AgentRunError, StudentSupportAgent
from student_support_agent.config import (
    ConfigurationError,
    load_settings,
    project_data_directory,
)

MAX_QUESTION_CHARS = 2_000

app = Flask(__name__)
# Reject oversized request bodies before they reach the agent.
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.get("/")
def index():
    return render_template("index.html", max_chars=MAX_QUESTION_CHARS)


@app.post("/api/ask")
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()[:MAX_QUESTION_CHARS]
    if not question:
        return jsonify(error="Enter a non-sensitive policy question first."), 400

    try:
        settings = load_settings()
        result = StudentSupportAgent(settings, project_data_directory()).respond(question)
    except ConfigurationError as exc:
        return jsonify(error=f"Configuration error: {exc}"), 500
    except AgentRunError as exc:
        return jsonify(error=f"Agent error: {exc}"), 502

    metrics = result.metrics
    return jsonify(
        answer=result.answer,
        latency_ms=metrics.latency_ms,
        prompt_tokens=metrics.prompt_tokens,
        completion_tokens=metrics.completion_tokens,
        tools=[{"name": t.name, "status": t.status} for t in metrics.tool_calls],
    )


if __name__ == "__main__":
    # Local use only: bound to localhost, debug off so errors never leak details.
    app.run(host="127.0.0.1", port=5000, debug=False)
