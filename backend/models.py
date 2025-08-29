"""
This module defines the data models used by the news agent backend.

The application maintains a simple in‑memory session store to track a
conversation. Each session keeps track of the user's collected
preferences and the conversation history. In a production system you
would likely persist sessions to a database or a distributed cache,
but for the purposes of this exercise an in‑memory dictionary is
sufficient.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid


@dataclass
class Message:
    """Represents a single chat message.

    role: "user" or "assistant".
    content: the textual content of the message.
    """

    role: str
    content: str


@dataclass
class Session:
    """Represents a chat session.

    Each session has a unique identifier, a set of collected
    preferences and a conversation history. Preferences are stored
    under well defined keys which map to the five questions defined in
    the problem statement. The `question_index` attribute tracks
    progress through the question flow.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    preferences: Dict[str, Optional[str]] = field(default_factory=lambda: {
        "tone_of_voice": None,
        "response_format": None,
        "language": None,
        "interaction_style": None,
        "news_topics": None,
    })
    conversation: List[Message] = field(default_factory=list)
    # Index of the next question to ask. Range 0‑4 inclusive. When
    # question_index == len(QUESTIONS), all preferences are collected.
    question_index: int = 0

    def is_complete(self) -> bool:
        """Return True if all preferences have been filled."""
        return all(v for v in self.preferences.values())

    def record_answer(self, answer: str) -> None:
        """Record the user's answer to the current question.

        This method will map the answer to the appropriate preference
        key based on the current question index and then advance the
        question pointer.
        """
        keys = list(self.preferences.keys())
        if self.question_index < len(keys):
            key = keys[self.question_index]
            self.preferences[key] = answer.strip()
            self.question_index += 1

    def next_question(self) -> Optional[str]:
        """Return the next question text, or None if complete."""
        from .services import QUESTIONS
        if self.question_index < len(QUESTIONS):
            return QUESTIONS[self.question_index]
        return None


class SessionStore:
    """A simple in‑memory store for sessions.

    Keys are session ids and values are Session objects.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}

    def create(self) -> Session:
        session = Session()
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def reset(self, session_id: str) -> Optional[Session]:
        """Reset the session preferences and question index.

        Conversation history is left intact. To completely clear a
        session remove it from the store and create a new one.
        """
        session = self._sessions.get(session_id)
        if session:
            session.preferences = {
                "tone_of_voice": None,
                "response_format": None,
                "language": None,
                "interaction_style": None,
                "news_topics": None,
            }
            session.question_index = 0
        return session