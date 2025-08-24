"""
FastAPI application for the Latest News backend.

This module sets up a minimal HTTP API exposing two endpoints:

* GET `/health` – returns a simple JSON payload to indicate the
  service is running.
* POST `/chat` – accepts a chat request containing the user's
  message and a snapshot of their preferences, orchestrates the
  agent to fetch and summarise news using mock data, and streams
  the results back to the caller as Server‑Sent Events (SSE).

The implementation deliberately avoids any external network calls
when `MOCK_MODE` is enabled. In this example environment, the
necessary packages such as `python-dotenv`, `openai` and
`tenacity` are not installed. Therefore the agent uses simple
heuristics to decide which tool to call and returns deterministic
mock responses for demonstration and testing purposes.

The event stream yields JSON objects one per line. Each object
contains a `type` field indicating the kind of event (e.g.
`tool_call`, `tool_result`, `content`). A final `done` event
signals the end of the stream.
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent.schemas import ChatRequest
from agent.runtime import run_agent


app = FastAPI(title="Latest News Agent API")

# Allow all origins in development. In production you should
# restrict this to your frontend's domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, bool]:
    """Healthcheck endpoint returning a simple OK response."""
    return {"ok": True}


@app.post("/chat")
async def chat(body: ChatRequest, request: Request) -> StreamingResponse:
    """
    Chat endpoint implementing a very simple agent loop.

    It accepts a `ChatRequest` containing the session id, the user's
    message and a snapshot of their preferences. The agent function
    produces a list of events which are streamed back to the caller
    as SSE. Each event is serialised as JSON and sent on its own
    line prefixed by `data: ` as per the SSE specification.
    """
    async def event_stream() -> AsyncGenerator[str, None]:
        # Run the agent to obtain a sequence of events. Since our
        # implementation uses mock data, there are no external side
        # effects nor long running operations.
        events = await run_agent(body.message, body.prefs_snapshot)
        for ev in events:
            # Serialise the event dict to JSON. We use the standard
            # library's `json` module rather than third party
            # libraries such as orjson.
            yield f"data: {json.dumps(ev, default=str)}\n\n"
            # Briefly yield control back to the event loop. While not
            # strictly necessary here, it improves responsiveness in
            # real applications.
            await asyncio.sleep(0)
        # Indicate the end of the stream. Clients should stop
        # listening after receiving this event.
        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")