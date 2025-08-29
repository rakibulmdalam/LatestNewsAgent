"""
Entry point for the backend service. This module creates a FastAPI
application, configures middleware, and registers routers. The app can
be run with `uvicorn backend.main:app --reload` during development.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import chat


app = FastAPI(title="Latest News Agent")

# Allow the frontend to communicate with the backend. In a production
# setting these origins should be restricted to known domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

# A simple health check endpoint
@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}