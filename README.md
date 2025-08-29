# Latest News Agent

This repository contains a simple full–stack application that
implements a conversational news agent. The goal of the project is
to collect a user’s preferences through a chat interface and then
deliver news summaries that reflect those choices. It follows a clean
architecture with separate modules for models, services and routes
on the backend. The frontend is built with **Next.js** and React and
uses the Inter font for a modern look.

## Features

- **Backend (Python/FastAPI)**
  - Maintains chat sessions and user preferences in an in‑memory
    store.
  - Asks a fixed set of preference questions (tone of voice, response
    format, language, interaction style and news topics) before
    generating any news.
  - Generates customised news summaries from a dummy data set. If a
    local `ollama` installation with the `phi3` model is available the
    service will use it to rewrite the summaries. Otherwise it falls
    back to simple string transformations (bullet points, tone
    adjustments, etc.).
  - Supports commands to deliver additional articles (`more`/`next`) or
    restart the preference collection (`reset`).
  - CORS is enabled for all origins and the static frontend files are
    served directly from the backend.

- **Frontend (Vanilla JS)**
  - Presents a clean, light‑coloured chat interface with Inter font.
  - Shows a visual checklist of the five preference questions and
    marks each item complete as the user answers.
  - Sends user messages to the backend and displays assistant
    responses in chat bubbles.
  - Handles pressing Enter to send messages and provides a simple Send
    button.

## Getting Started

### Prerequisites

- **Backend**: Python 3.8 or higher.
- **Frontend**: Node.js 16 or later. The frontend uses Next.js and React, so you will need npm or yarn to install dependencies.
- Optionally, install [Ollama](https://ollama.ai/) with the `phi3`
  model if you wish to experiment with AI‑generated rewriting of news
  articles.

### Installation

1. Clone the repository or copy its contents.
2. **Backend**
   1. (Optional) Create and activate a virtual environment.
   2. Install the Python dependencies from `backend/requirements.txt`:

      ```bash
      pip install -r backend/requirements.txt
      ```
3. **Frontend**
   1. Navigate into the `frontend` directory.
   2. Install the Node dependencies:

      ```bash
      npm install
      ```

### Running the Application

1. **Start the backend server** from the repository root:

   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

   The backend exposes REST endpoints under `/session` for managing chat
   sessions and is CORS‑enabled, so it can be reached from a separate
   frontend running on another port.

2. **Start the frontend**. In a new terminal window, navigate into the
   `frontend` directory and run:

   ```bash
   npm run dev
   ```

   This will start the Next.js development server on port 3000. Open
   your browser to `http://localhost:3000` and you will see the chat
   interface. The agent will begin by asking you about your preferred
   tone of voice.

3. Answer each question. After all preferences are collected the
   agent will display a few dummy news summaries tailored to your
   choices. You can type `more` to receive more articles or `reset`
   to restart the question flow.

### Notes on AI Integration

If you have `ollama` installed and a `phi3` model available the
backend will attempt to call it to rewrite the dummy news articles in
line with the collected preferences. The command used is roughly:

```bash
ollama run phi3
```

and the prompt includes the tone, format, language and interaction
style. If `ollama` is not found on your system the service falls back
to a simple implementation that supports bullet points and
enthusiastic tones.

## Project Structure

```
.
├── backend
│   ├── main.py           # FastAPI application entry point
│   ├── models.py         # Session and message data models
│   ├── routes
│   │   └── chat.py       # REST endpoints for chat interactions
│   └── services
│       ├── __init__.py   # Shared constants (preference questions)
│       └── news_service.py # Dummy news retrieval and formatting logic
├── frontend
│   ├── index.html        # Chat interface markup
│   ├── style.css         # Styles for chat and preferences UI
│   └── script.js         # Client‑side logic to talk to the backend
└── README.md             # This readme
```

The modular layout makes it straightforward to extend the agent. For
example, you could swap out the dummy news source for a real API or
add persistent storage for sessions. Similarly, the frontend could be
rewritten using your favourite JavaScript framework without changing
the backend.