"""
Shared constants and utility functions for the services layer.

The services layer contains logic for retrieving and transforming
content. In our case, because external APIs such as Exa are not
available, we generate sample news items locally. A real
implementation would fetch data from third‑party APIs.
"""

from typing import List

# The ordered list of questions to collect user preferences. These
# correspond directly to the keys defined in models.Session.preferences.
QUESTIONS: List[str] = [
    "What is your preferred tone of voice? For example: formal, casual or enthusiastic.",
    "What is your preferred response format? For example: bullet points or paragraphs.",
    "Which language would you like your news summaries in?", 
    "How detailed would you like the summaries? For example: concise or detailed.",
    "What topics are you interested in? For example: technology, sports, politics.",
]