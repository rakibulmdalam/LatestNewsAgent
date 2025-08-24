"""
Stub definitions for OpenAI API integration.

In the full implementation of this project, this module would
provide asynchronous helpers for interacting with OpenAI's chat
completion API to support raw tool calling and streaming outputs.
However, the current environment does not have the `openai` package
installed and network access is disabled, so these functions are
provided as stubs that either return `NotImplementedError` or
perform no operation. They serve to illustrate the intended API
surface without introducing import errors at runtime.
"""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List


async def chat_with_tools(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Stub for sending a chat completion request with tool calling.

    In a production system, this would forward the list of messages
    to OpenAI's API and return the assistant's response. Here it
    raises a `NotImplementedError` because external API access is
    unavailable. The agent does not call this function when
    `MOCK_MODE` is enabled.
    """
    raise NotImplementedError(
        "chat_with_tools is not implemented in the mock environment"
    )


async def stream_final_answer(messages: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
    """
    Stub for streaming the final assistant answer.

    In the real implementation this would stream token deltas from
    OpenAI. Here it yields nothing and immediately returns.
    """
    if False:
        yield  # This is never executed but satisfies type checkers.
    return


async def summarize_articles(*args: Any, **kwargs: Any) -> str:
    """
    Stub for summarising articles via a language model.

    This function would normally call OpenAI's API to produce a
    summary according to the user's preferences. In this mock
    environment it simply raises to signal it should not be used.
    """
    raise NotImplementedError(
        "summarize_articles is not implemented in the mock environment"
    )