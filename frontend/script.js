// Frontend logic for the Latest News Agent chat interface.
//
// This script handles session creation, sending messages to the backend
// and updating the user interface. It uses ES module syntax so it can
// be imported directly via <script type="module"> without a bundler.

let sessionId = null;
// Track completion of preferences. The keys correspond to those
// defined on the backend. When a preference is answered the value is
// set to true.
const preferenceKeys = [
  'tone_of_voice',
  'response_format',
  'language',
  'interaction_style',
  'news_topics',
];
const preferencesState = {};
preferenceKeys.forEach((key) => {
  preferencesState[key] = false;
});

// Cache DOM elements
const chatHistoryEl = document.getElementById('chat-history');
const messageInputEl = document.getElementById('message-input');
const sendButtonEl = document.getElementById('send-button');

// Append a chat message to the history. The role should be either
// 'user' or 'assistant'. This function creates a list item with a
// styled bubble.
function addMessage(role, text) {
  const li = document.createElement('li');
  const div = document.createElement('div');
  div.classList.add('message', role);
  div.textContent = text;
  li.appendChild(div);
  chatHistoryEl.appendChild(li);
  // Scroll to the bottom to show the latest message
  chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
}

// Update the preferences checklist based on the current state. When a
// preference is complete its list item receives the 'completed' class.
function updateChecklist() {
  preferenceKeys.forEach((key) => {
    const li = document.getElementById(`pref-${key}`);
    if (preferencesState[key]) {
      li.classList.add('completed');
    } else {
      li.classList.remove('completed');
    }
  });
}

// Start a new session by calling the backend. Once the session is
// created the first question will be displayed.
async function createSession() {
  try {
    const res = await fetch('/session', { method: 'POST' });
    if (!res.ok) {
      throw new Error(`Failed to create session: ${res.status}`);
    }
    const data = await res.json();
    sessionId = data.session_id;
    // Reset preferences state
    preferenceKeys.forEach((key) => {
      preferencesState[key] = false;
    });
    updateChecklist();
    addMessage('assistant', data.message);
  } catch (err) {
    console.error(err);
    addMessage('assistant', 'Oops! Unable to start a session.');
  }
}

// Send a user message to the backend. The backend will respond with
// one or more assistant messages and potentially an updated
// preferences object.
async function sendMessage() {
  const text = messageInputEl.value.trim();
  if (!text || !sessionId) {
    return;
  }
  addMessage('user', text);
  messageInputEl.value = '';
  try {
    const res = await fetch(`/session/${sessionId}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }
    const data = await res.json();
    data.responses.forEach((msg) => {
      addMessage('assistant', msg);
    });
    // Update preferences state
    if (data.preferences) {
      preferenceKeys.forEach((key) => {
        preferencesState[key] = Boolean(data.preferences[key]);
      });
      updateChecklist();
    }
  } catch (err) {
    console.error(err);
    addMessage('assistant', 'There was an error processing your request.');
  }
}

// Attach event listeners
sendButtonEl.addEventListener('click', sendMessage);
messageInputEl.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    sendMessage();
  }
});

// Kick off the session when the page loads
createSession();