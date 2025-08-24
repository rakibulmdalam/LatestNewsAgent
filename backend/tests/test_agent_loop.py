"""
Integration tests for the simplified agent loop.

These tests exercise the `run_agent` function directly with
mock preferences to verify that it produces a coherent event
sequence. Only mock mode is tested because external API calls are
not available in this environment.
"""

import asyncio

from agent.schemas import Preferences
from agent.runtime import run_agent


def test_run_agent_with_news_request(monkeypatch):
    """The agent should fetch and summarise news when 'news' is mentioned."""
    monkeypatch.setenv("MOCK_MODE", "true")
    prefs = Preferences(tone="casual", format="bullets", interaction="concise")
    message = "Latest news on artificial intelligence"
    events = asyncio.run(run_agent(message, prefs))
    # Expect at least five events: tool_call, tool_result, tool_call, tool_result, content
    assert len(events) >= 5
    assert events[0]["type"] == "tool_call" and events[0]["name"] == "exa_news_fetcher"
    assert events[1]["type"] == "tool_result" and events[1]["name"] == "exa_news_fetcher"
    assert events[2]["type"] == "tool_call" and events[2]["name"] == "news_summarizer"
    assert events[3]["type"] == "tool_result" and events[3]["name"] == "news_summarizer"
    assert events[-1]["type"] == "content"
    # The final summary should mention the greeting and include bullet points
    summary_text = events[-1]["text"]
    assert "here's" in summary_text.lower() or "here is" in summary_text.lower()
    assert "- " in summary_text, "Expected bullet points in the summary"


def test_run_agent_without_news(monkeypatch):
    """When the message does not request news, the agent should echo the input."""
    monkeypatch.setenv("MOCK_MODE", "true")
    prefs = Preferences()
    message = "Tell me a joke"
    events = asyncio.run(run_agent(message, prefs))
    assert len(events) == 1
    assert events[0]["type"] == "content"
    assert message in events[0]["text"]