"""
Pydantic models used throughout the backend.

These schemas define the structure of requests and responses for
the API, as well as internal data structures such as articles
returned from the news fetcher. Using Pydantic ensures data is
validated and serialized consistently.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, AnyHttpUrl, Field


class Preferences(BaseModel):
    """User preference snapshot.

    All fields are optional; the agent can prompt the user for
    missing preferences. Tone may be one of 'formal', 'casual' or
    'enthusiastic'. Format may be 'bullets' or 'paragraphs'.
    Interaction indicates whether responses should be concise or
    detailed. Topics is a list of strings representing subject
    areas of interest.
    """

    tone: Optional[Literal["formal", "casual", "enthusiastic"]] = None
    format: Optional[Literal["bullets", "paragraphs"]] = None
    language: Optional[str] = None
    interaction: Optional[Literal["concise", "detailed"]] = None
    topics: Optional[List[str]] = None


class ChatRequest(BaseModel):
    """Request body for the `/chat` endpoint."""

    session_id: str = Field(..., description="Unique identifier for the chat session")
    message: str = Field(..., description="The user's message or query")
    prefs_snapshot: Preferences = Field(..., description="Snapshot of the user's current preferences")


class Article(BaseModel):
    """Representation of a news article.

    Only the title and URL are strictly required. Snippet contains a
    short excerpt from the article body. Published date is optional
    because mock articles may not set it. Source indicates the
    domain or outlet that published the piece.
    """

    title: str
    url: AnyHttpUrl
    snippet: Optional[str] = None
    published_at: Optional[datetime] = None
    source: Optional[str] = None


class FetchParams(BaseModel):
    """Parameters for the news fetcher tool."""

    query: str = Field(..., description="Topic or search query")
    num_results: int = Field(5, ge=1, le=20, description="Number of articles to return")
    recency_days: int = Field(7, ge=1, description="How many days back to search")