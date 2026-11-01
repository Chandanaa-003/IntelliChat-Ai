# IntelliChat AI - Modern Production-Ready AI Chatbot Application

An enterprise-grade, intelligent AI chatbot application with real-time Server-Sent Events (SSE) streaming, context memory, multi-provider LLM support, JWT authentication, and a sleek dark/light user interface.

![Tech Stack](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-blue)
![Styling](https://img.shields.io/badge/Styling-Tailwind%20CSS-38bdf8)
![Backend](https://img.shields.io/badge/Backend-FastAPI%20%28Python%203.10%2B%29-009688)
![ORM](https://img.shields.io/badge/Database-SQLAlchemy%202.0%20Async-red)
![Database](https://img.shields.io/badge/Supported%20DB-PostgreSQL%20%2F%20SQLite-336791)

---

## ✨ Features

### 1. Modern Chat Interface
- **Responsive Layout**: Designed for mobile, tablet, and widescreen desktop experiences.
- **Dark & Light Modes**: Curated HSL color palette with smooth transitions and persistent state.
- **Real-Time Token Streaming**: Immediate visual feedback as responses are generated token-by-token.
- **Typing Indicators**: Subtle 3-dot pulse animation during thinking states.
- **Interactive Suggestions**: Quick prompt starter cards for instant exploration.

### 2. AI Intelligence & Conversation Memory
- **Context Retention**: Maintains multi-turn conversation history within an intelligent token sliding window.
- **Follow-up Handling**: Seamlessly understands references to previous code snippets and topics.
- **Pluggable LLM Engine**:
  - **Groq LPU**: Ultra-fast inference with Llama 3.1 models.
  - **OpenAI / OpenRouter**: Support for GPT-3.5, GPT-4, and custom endpoints.
  - **Hugging Face**: Serverless inference via Hugging Face Router.
  - **Smart Offline Assistant**: Works 100% out-of-the-box even without external API keys!

### 3. Developer & Power-User Tools
- **Markdown & Syntax Highlighting**: Clean typography with headers, lists, blockquotes, and tables.
- **Code Block Actions**: Language badge and one-click copy to clipboard with status feedback.
- **Message Regeneration**: Re-runs the assistant response on demand.
- **Session Management**: Create, rename, search, and delete multiple chat threads.
- **User Authentication**: Secure JWT-based authentication (Register / Sign In) with seamless Guest Mode.

---

## 🏗️ Architecture & Directory Structure

```plaintext
ai_chaatboot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py          # Register, Login, Me endpoints
│   │   │   │   ├── chat.py          # SSE Streaming, Regeneration, Model Catalog
│   │   │   │   ├── conversations.py # Session CRUD, Search, Message History
│   │   │   │   └── router.py        # Bundled v1 API router
│   │   │   └── deps.py              # JWT Bearer dependency injection
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic v2 environment settings loader
│   │   │   ├── database.py          # Async SQLAlchemy engine & session factory
│   │   │   └── security.py          # Bcrypt hashing & JWT encoding/decoding
│   │   ├── models/                  # SQLAlchemy ORM models (User, Conversation, Message)
│   │   ├── schemas/                 # Pydantic v2 validation models
│   │   ├── services/
│   │   │   ├── auth_service.py      # User authentication business logic
│   │   │   ├── chat_service.py      # Context window aggregation & SSE orchestrator
│   │   │   ├── conversation_service.py # Database session queries & mutations
│   │   │   └── llm/                 # LLM provider abstraction (Base, Mock, OpenAI, Groq, HF)
│   │   └── main.py                  # FastAPI application entry point & CORS
│   ├── tests/                       # Automated pytest test suites (Phase 1, 2, 3)
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Sample configuration
│   └── run.py                       # Easy execution script
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/AuthModal.tsx    # Tabbed Sign In / Register dialog
│   │   │   ├── chat/
│   │   │   │   ├── ChatHeader.tsx    # Header with title editing & actions
│   │   │   │   ├── ChatInput.tsx     # Auto-growing multiline input with stop button
│   │   │   │   ├── CodeBlock.tsx     # Syntax formatted block with copy action
│   │   │   │   ├── MessageItem.tsx   # Markdown renderer with message actions
│   │   │   │   ├── MessageList.tsx   # Auto-scrolling list with starter cards
│   │   │   │   └── TypingIndicator.tsx
│   │   │   └── layout/
│   │   │       ├── ModelSelector.tsx # Provider & model dropdown
│   │   │       ├── Sidebar.tsx       # Conversation history, search, and user profile
│   │   │       └── ThemeToggle.tsx   # Smooth Sun/Moon theme switcher
│   │   ├── context/                  # React Contexts (Auth, Chat, Theme)
│   │   ├── services/api.ts           # Fetch API client + SSE reader
│   │   ├── types/index.ts            # TypeScript definitions
│   │   ├── App.tsx                   # Main layout container
│   │   └── index.css                 # Tailwind directives & custom scrollbars
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
└── README.md
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Node.js**: v18.0+ or v20.0+ (Tested on v24)
- **Python**: v3.10+ (Tested on v3.10.9)
- **Git** (optional)

---

### Step 1: Backend Setup

1. Open a terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows:
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment variables:
   ```bash
   cp .env.example .env
   ```
   *(By default, `DATABASE_URL` is configured to `sqlite+aiosqlite:///./chatbot.db` for instant, zero-configuration local execution!)*

5. *(Optional)* To connect to a **PostgreSQL** database:
   Update `DATABASE_URL` in `backend/.env`:
   ```env
   DATABASE_URL="postgresql+asyncpg://postgres:your_password@localhost:5432/chatbot"
   ```

6. Start the FastAPI server:
   ```bash
   python run.py
   ```
   - Server runs on: `http://localhost:8000`
   - Interactive Swagger API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

---

### Step 2: Frontend Setup

1. Open a second terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - Frontend runs on: `http://localhost:5173`

4. Open `http://localhost:5173` in your browser to experience IntelliChat!

---

## 🔑 LLM Provider Setup

```env
# Select a provider and model in backend/.env
DEFAULT_LLM_PROVIDER=ollama
DEFAULT_MODEL=qwen2.5:3b
OLLAMA_BASE_URL=http://localhost:11434
```

The default setup uses Ollama locally. Start Ollama and pull the configured model before chatting:

```powershell
ollama pull qwen2.5:3b
```

The model selector also includes the built-in `Smart Assistant`, which works offline. To use a hosted provider, configure its API key and update `DEFAULT_LLM_PROVIDER` and `DEFAULT_MODEL`, then restart the backend:

```env
# Groq
DEFAULT_LLM_PROVIDER=groq
DEFAULT_MODEL=llama-3.1-8b-instant
GROQ_API_KEY="gsk_..."

```

```env
# OpenAI
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini
OPENAI_API_KEY="sk-..."

```

```env
# Hugging Face
DEFAULT_LLM_PROVIDER=huggingface
DEFAULT_MODEL=Qwen/Qwen2.5-3B-Instruct
HUGGINGFACE_API_KEY="hf_..."
```

Only the selected provider and model are listed alongside the offline assistant. Provider connection or configuration failures are returned in the chat instead of being saved as a successful model response.

---

## 🧪 Automated Testing

All layers of the backend are covered with automated async integration tests:

```bash
cd backend
python -m pytest tests/ -v
```

Test Suites:
- `tests/test_phase1.py`: Configuration, database schema, async engine, and `/health`.
- `tests/test_phase2.py`: User registration, password hashing, JWT tokens, conversation CRUD, and message history.
- `tests/test_phase3.py`: Real-time Server-Sent Events (SSE) streaming, context memory, follow-ups, and message regeneration.

---

## 🛡️ Security & Production Best Practices

1. **Password Hashing**: Passwords are encrypted with `bcrypt` (12 rounds) and never stored in plain text.
2. **JWT Authentication**: Industry-standard JSON Web Tokens with configurable expiration and secret key signing.
3. **CORS Hardening**: Strict origin whitelisting via `.env`.
4. **Context Window Protection**: Automatic sliding window truncates older turns to avoid context overflow.
5. **Robust Non-blocking SSE**: Streaming responses run asynchronously without blocking worker threads.
