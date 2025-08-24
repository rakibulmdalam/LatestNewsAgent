"""
Prompt definitions for the agent.

In the real implementation, the system prompt would instruct the
language model to respect user preferences and decide when to call
tools. In this mock implementation we include it purely as a
configuration constant and do not actively use it because we
cannot make external API calls. It remains here to demonstrate
where such configuration would live in a production system.
"""

# System prompt describing the agent's behaviour. This constant
# persists across chat turns and informs the model how to
# structure responses and when to invoke tools. The variables
# enclosed in braces would be replaced with actual values when
# constructing prompts for the model.
SYSTEM_PROMPT = """
You are a Latest News Agent. Always respect user preferences:
- tone, format (bullets|paragraphs), language, interaction (concise|detailed), topics.
If topics are unknown and the user asks for news, ask the 5 preference questions briefly.
Decide when to call tools:
- exa_news_fetcher when you need fresh articles.
- news_summarizer to convert fetched articles into a preference-aligned brief.
Cite sources by domain and date inline. Keep answers succinct unless 'interaction' is 'detailed'.
"""