"""
Simple agent loop for the Latest News backend.

In a fully featured implementation this module would use OpenAI's
tool calling capabilities to decide whether to invoke external
functions. Since network access and the openai package are
unavailable here, this agent uses a very basic heuristic: if the
user's message mentions news or if topics are provided in the
preferences, it calls the news fetcher and summariser. Otherwise
it echoes the user's message back.

The agent returns a list of event dictionaries which the API
exposes over Server‑Sent Events. Each event has a `type` field
indicating its purpose:

* `tool_call` – the agent has decided to call a tool with the
  specified name and arguments.
* `tool_result` – the result of a tool call.
* `content` – the assistant's natural language response.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .schemas import Preferences, FetchParams, Article
from .tools import exa_news_fetcher, news_summarizer


async def run_agent(user_text: str, prefs: Preferences) -> List[Dict[str, Any]]:
    """
    Run a simplified agent loop on the given user input and preferences.

    This function decides, based on the user's message and the
    provided preferences, whether to fetch and summarise news. It
    constructs a sequence of events describing the tool invocations
    and final assistant message. The events can then be streamed
    back to the client via SSE.

    :param user_text: The raw input from the user.
    :param prefs: Snapshot of the user's preferences.
    :return: A list of event dictionaries.
    """
    events: List[Dict[str, Any]] = []

    # Determine whether we should fetch news. Simple heuristic: if
    # the message contains the word 'news' or 'latest', or if the
    # user has specified topics, then perform a fetch. This avoids
    # the need for external language model calls.
    lower_text = user_text.lower()
    wants_news = any(keyword in lower_text for keyword in ["news", "latest", "headlines"])
    has_topics = bool(prefs.topics and len(prefs.topics) > 0)

    if wants_news or has_topics:
        # Build a query string. If topics are provided, join them; otherwise
        # use the user's message verbatim.
        query = ", ".join(prefs.topics) if has_topics else user_text
        fetch_params = FetchParams(query=query, num_results=5)

        # Record the tool call event.
        events.append(
            {
                "type": "tool_call",
                "name": "exa_news_fetcher",
                "args": fetch_params.model_dump(),
            }
        )

        # Execute the news fetcher. In mock mode this returns
        # deterministic articles.
        articles = await exa_news_fetcher(fetch_params)

        # Record the tool result event with the raw article data.
        events.append(
            {
                "type": "tool_result",
                "name": "exa_news_fetcher",
                "result": {"articles": [a.model_dump() for a in articles]},
            }
        )

        # Prepare arguments for the summariser tool. Merge any
        # preferences passed from the caller; unspecified fields
        # default to None.
        sum_kwargs = {
            "tone": prefs.tone,
            "fmt": prefs.format,
            "language": prefs.language,
            "interaction": prefs.interaction,
        }

        # Record the summariser call. The model arguments are
        # intentionally minimal in this mock environment.
        events.append(
            {
                "type": "tool_call",
                "name": "news_summarizer",
                "args": {},
            }
        )

        summary = await news_summarizer(
            articles=articles,
            tone=sum_kwargs.get("tone"),
            fmt=sum_kwargs.get("fmt"),
            language=sum_kwargs.get("language"),
            interaction=sum_kwargs.get("interaction"),
        )

        # Record the summariser result.
        events.append(
            {
                "type": "tool_result",
                "name": "news_summarizer",
                "result": {"summary": summary},
            }
        )

        # Add the final assistant message using the summary as the
        # content. In a real implementation you might also include
        # citations or additional contextual information.
        events.append(
            {
                "type": "content",
                "text": summary,
            }
        )
    else:
        # If the user didn't ask for news, simply echo back the
        # message. This ensures the frontend receives something to
        # display rather than an empty event list.
        events.append(
            {
                "type": "content",
                "text": f"You said: {user_text}",
            }
        )

    return events