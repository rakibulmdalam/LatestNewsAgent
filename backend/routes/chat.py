"""
Routes for chat sessions. This module defines the HTTP endpoints that
the frontend interacts with. Using POST requests rather than websockets
simplifies the implementation while still supporting conversational
interaction.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..models import Message, Session, SessionStore
from ..services.news_service import generate_news_response
from ..services import QUESTIONS


router = APIRouter(prefix="/session")

session_store = SessionStore()


class CreateSessionResponse(BaseModel):
    session_id: str
    message: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    responses: List[str]
    preferences_complete: bool
    preferences: Optional[dict] = None


@router.post("", response_model=CreateSessionResponse)
async def create_session() -> CreateSessionResponse:
    """Create a new chat session.

    Returns the new session ID and the first question to ask.
    """
    session = session_store.create()
    first_question = QUESTIONS[0]
    # Add to conversation history
    session.conversation.append(Message(role="assistant", content=first_question))
    return CreateSessionResponse(session_id=session.id, message=first_question)


@router.post("/{session_id}/message", response_model=ChatResponse)
async def chat(session_id: str, request: ChatRequest) -> ChatResponse:
    """Handle a user message for a given session.

    Depending on the current state of preference collection this
    endpoint will either store the answer, ask the next question, or
    provide news summaries. Special commands 'reset' and 'more' are
    supported to restart the preference flow or request more news
    articles respectively.
    """
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_input = request.message.strip()
    session.conversation.append(Message(role="user", content=user_input))

    responses: List[str] = []
    # Handle special commands
    if user_input.lower() == "reset":
        session_store.reset(session_id)
        next_q = session.next_question()
        if next_q:
            responses.append(next_q)
            session.conversation.append(Message(role="assistant", content=next_q))
        return ChatResponse(responses=responses, preferences_complete=False, preferences=session.preferences)
    if user_input.lower() in {"more", "next", "another"}:
        # Provide more news items using existing preferences
        if session.is_complete():
            news = generate_news_response(session.preferences)
            responses.append(news)
            session.conversation.append(Message(role="assistant", content=news))
            return ChatResponse(responses=responses, preferences_complete=True, preferences=session.preferences)
        else:
            # Not ready yet: prompt next question
            next_q = session.next_question()
            if next_q:
                responses.append(next_q)
                session.conversation.append(Message(role="assistant", content=next_q))
            return ChatResponse(responses=responses, preferences_complete=False, preferences=session.preferences)

    # If preferences not complete, record answer and ask next question
    if not session.is_complete():
        session.record_answer(user_input)
        next_q = session.next_question()
        if next_q:
            responses.append(next_q)
            session.conversation.append(Message(role="assistant", content=next_q))
            return ChatResponse(responses=responses, preferences_complete=False, preferences=session.preferences)
        # All preferences collected after this answer
        news = generate_news_response(session.preferences)
        responses.append(news)
        session.conversation.append(Message(role="assistant", content=news))
        return ChatResponse(responses=responses, preferences_complete=True, preferences=session.preferences)

    # At this point preferences are complete. Any other input is
    # treated as a request for more articles.
    news = generate_news_response(session.preferences)
    responses.append(news)
    session.conversation.append(Message(role="assistant", content=news))
    return ChatResponse(responses=responses, preferences_complete=True, preferences=session.preferences)