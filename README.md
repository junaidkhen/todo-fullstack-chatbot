# Todo AI Chatbot

A multi-phase todo list application featuring an AI-powered chat interface for natural language task management. Built with Next.js, FastAPI, and Google Gemini AI.

## Overview

This project demonstrates a full-stack todo application developed in three phases:

- **Phase I**: In-memory console application (TypeScript/Bun)
- **Phase II**: Full-stack web application with authentication (Next.js + FastAPI)
- **Phase III**: AI-powered chat interface for task management (Gemini API)

## Features

- **Multi-User Authentication** - Secure sign-up and sign-in with Better Auth
- **Task Management** - Create, view, update, complete, and delete tasks
- **AI Chat Interface** - Natural language task management via Gemini AI
- **User Isolation** - Strict data separation between users
- **Persistent Storage** - Tasks stored in Neon PostgreSQL database
- **Responsive UI** - Works on mobile, tablet, and desktop devices

---

## Prerequisites

Before starting, ensure you have:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Node.js | 20.x+ | `node --version` |
| npm | 10.x+ | `npm --version` |
| Python | 3.13+ | `python --version` |
| Git | 2.x+ | `git --version` |
| PostgreSQL | 15+ (or Neon) | [neon.tech](https://neon.tech) |
| Gemini API Key | - | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/todo-fullstack.git
cd todo-fullstack
```

### 2. Set up backend (Python/FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure backend environment

```bash
cp .env.example .env
# Edit .env with your database URL, auth secret, and Gemini API key
```

### 4. Set up frontend (Next.js)

```bash
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local with matching auth secret
```

### 5. Start both servers

```bash
# Terminal 1 (Backend):
cd backend && source .venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 (Frontend):
cd frontend
npm run dev
```

### Verification

After setup, verify the application is running:

| Endpoint | URL | Expected Result |
|----------|-----|-----------------|
| Frontend | http://localhost:3000 | Login page |
| Backend API | http://localhost:8000/docs | Swagger UI |
| Chat Interface | http://localhost:3000/chat | AI chat (after login) |

---

## Environment Variables

### Backend (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (async) | `postgresql+asyncpg://user:pass@host:5432/db` |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (32+ characters) | Generate with `openssl rand -base64 32` |
| `GEMINI_API_KEY` | Yes | Google Gemini API key | Get from [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `CORS_ORIGINS` | Yes | Allowed frontend origins | `http://localhost:3000` |
| `DEBUG` | No | Enable debug logging | `True` |

### Frontend (.env.local)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL | `http://localhost:8000` |
| `BETTER_AUTH_SECRET` | Yes | Must match backend secret exactly | Same as backend |
| `NEXT_PUBLIC_DEBUG` | No | Enable debug mode | `true` |

> **Important**: The `BETTER_AUTH_SECRET` must be identical in both backend and frontend for authentication to work.

---

## Project Structure

```
todo-fullstack/
├── console/              # Phase I: In-memory console app (TypeScript/Bun)
│   ├── src/             # Console app source
│   └── package.json     # Console dependencies
│
├── frontend/             # Phase II/III: Next.js web app + Chat UI
│   ├── src/
│   │   ├── app/         # App Router pages (signup, signin, tasks, chat)
│   │   ├── components/  # React components (TaskList, TaskForm, ChatWindow)
│   │   └── lib/         # Utilities (auth, api)
│   ├── package.json
│   └── .env.example
│
├── backend/              # Phase II/III: FastAPI backend + Gemini integration
│   ├── src/
│   │   ├── models/      # SQLModel database models (Task, Conversation, Message)
│   │   ├── api/         # FastAPI route handlers (tasks.py, chat.py)
│   │   ├── auth/        # JWT validation logic
│   │   ├── gemini/      # Gemini AI integration and tools
│   │   └── database.py  # Database connection management
│   ├── main.py          # FastAPI app entry point
│   ├── requirements.txt
│   └── .env.example
│
├── specs/                # Feature specifications (Spec-Driven Development)
│   ├── phase1/          # Phase I constitution
│   ├── phase2/          # Phase II constitution
│   ├── phase3/          # Phase III constitution
│   └── ###-feature/     # Per-feature specs (spec.md, plan.md, tasks.md)
│
├── history/
│   ├── prompts/         # Prompt History Records (PHRs)
│   └── adr/             # Architecture Decision Records
│
├── .specify/            # SpecKit Plus templates and scripts
├── CLAUDE.md            # Agent instructions
└── README.md            # This file
```

### Directory Descriptions

| Directory | Phase | Purpose |
|-----------|-------|---------|
| `console/` | I | Standalone console todo app with in-memory storage |
| `frontend/` | II/III | Next.js web application with auth and chat UI |
| `backend/` | II/III | FastAPI REST API with PostgreSQL and Gemini AI |
| `specs/` | All | Specification documents driving development |
| `history/` | All | Development history and architectural decisions |

### Where to Add New Code

| Type | Location | Example |
|------|----------|---------|
| API Endpoints | `backend/src/api/` | Add new routes in `*.py` files |
| React Components | `frontend/src/components/` | Create `*.tsx` component files |
| Database Models | `backend/src/models/` | Add SQLModel classes |
| App Pages | `frontend/src/app/` | Create new route directories |

---

## Chat Examples

After logging in and navigating to `/chat`, you can manage tasks using natural language:

### Adding a Task

```
You: "Add a task to buy groceries"
TaskBot: "Task added: 'Buy groceries'. What else can I help with?"
```

### Listing Tasks

```
You: "Show me my tasks"
TaskBot: "Here are your tasks:
1. Buy groceries (pending)
2. Finish homework (pending)"
```

### Completing a Task

```
You: "Mark 'buy groceries' as done"
TaskBot: "Great job! 'Buy groceries' is now complete."
```

### Updating a Task

```
You: "Change 'Finish homework' to 'Finish math homework'"
TaskBot: "Task updated: 'Finish math homework'"
```

### Deleting a Task

```
You: "Delete the 'Finish math homework' task"
TaskBot: "Task 'Finish math homework' has been deleted."
```

---

## API Endpoints

### Authentication (via Better Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create new user |
| POST | `/api/auth/signin` | Sign in existing user |
| POST | `/api/auth/signout` | Sign out user |

### Task Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List user's tasks |
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks/{id}` | Get specific task |
| PUT | `/api/tasks/{id}` | Update task |
| PATCH | `/api/tasks/{id}/toggle` | Toggle completion status |
| DELETE | `/api/tasks/{id}` | Delete task |

### Chat (Phase III)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message to AI assistant |

---

## Running Tests

### Backend Tests

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Troubleshooting

### Frontend can't connect to backend

- **Symptom**: API requests fail, "Network Error" in console
- **Solutions**:
  - Verify both servers are running (`localhost:3000` and `localhost:8000`)
  - Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` is `http://localhost:8000`
  - Ensure `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`
  - Restart both servers after changing environment variables

### Authentication fails

- **Symptom**: Login succeeds but API returns 401 Unauthorized
- **Solutions**:
  - Ensure `BETTER_AUTH_SECRET` is **identical** in both `.env` files
  - Restart both servers after changing secrets
  - Clear browser cookies and localStorage
  - Check that the secret is at least 32 characters

### Database connection errors

- **Symptom**: "Connection refused" or "Database not found"
- **Solutions**:
  - Verify PostgreSQL is running and accessible
  - Check `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:5432/db`
  - For Neon: ensure SSL is enabled (add `?sslmode=require` to URL)
  - Test connection with `psql` directly

### AI chat not responding

- **Symptom**: Messages sent but no AI response
- **Solutions**:
  - Verify `GEMINI_API_KEY` is set in `backend/.env`
  - Check backend logs for Gemini API errors
  - Ensure you're logged in (authentication required for chat)
  - Get a new API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Rate limiting errors

- **Symptom**: "Rate limit exceeded" or 429 responses
- **Solutions**:
  - Gemini free tier: 5-15 requests per minute
  - Wait 60 seconds and retry
  - Keep conversations focused to reduce API calls
  - Consider upgrading to paid tier for production

### Port conflicts

- **Symptom**: "Address already in use" error
- **Solutions**:
  - Find process using the port: `lsof -i :3000` or `lsof -i :8000`
  - Kill the process: `kill -9 <PID>`
  - Or use alternative ports:
    - Backend: `uvicorn main:app --reload --port 8001`
    - Frontend: `npm run dev -- -p 3001`
  - Update environment variables to match new ports

---

## Development

### Code Quality

- **Frontend**: TypeScript strict mode, ESLint, Prettier
- **Backend**: Python type hints, Black formatting, mypy
- **Testing**: Pytest for backend, Jest for frontend
- **Security**: JWT validation, SQL injection prevention

### Adding New Features

1. Update data models in `backend/src/models/` if needed
2. Add API endpoints in `backend/src/api/`
3. Create React components in `frontend/src/components/`
4. Update Next.js pages in `frontend/src/app/`
5. Write tests in respective test directories
6. Update documentation

---

## Contributing

This project follows Spec-Driven Development practices:

1. Review specifications in `specs/` directory
2. Follow the implementation plan in feature `plan.md`
3. Add tests for new functionality
4. Update documentation as needed

---

## License

This project was created as part of a coding exercise. Feel free to use and modify as needed.

## Credits

Built with:

- **Frontend**: Next.js 16+, React, TypeScript, Tailwind CSS, Better Auth
- **Backend**: FastAPI, Python 3.13+, SQLModel, asyncpg
- **Database**: PostgreSQL (Neon serverless)
- **AI**: Google Gemini API
- **Development**: Following Spec-Driven Development methodology
"# todo-fullstack-chatbot" 
