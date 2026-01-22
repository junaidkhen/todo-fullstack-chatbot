# Quick Start Reference Document

**Feature**: 010-deliverables-repo-structure
**Purpose**: Implementation reference for README.md quick start section

---

## Quick Start (5 Commands)

This section provides a streamlined setup process that can be completed in under 15 minutes.

### Prerequisites Checklist

Before starting, ensure you have:
- [ ] Node.js 20.x or later (`node --version`)
- [ ] npm 10.x or later (`npm --version`)
- [ ] Python 3.13 or later (`python --version`)
- [ ] Git 2.x or later (`git --version`)
- [ ] Access to Neon PostgreSQL (free tier at neon.tech)
- [ ] Gemini API key (free at aistudio.google.com/apikey)

### 5-Command Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/todo-fullstack.git
cd todo-fullstack

# 2. Set up backend (Python/FastAPI)
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure backend environment
cp .env.example .env
# Edit .env with your database URL, auth secret, and Gemini API key

# 4. Set up frontend (Next.js)
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local with matching auth secret

# 5. Start both servers
# Terminal 1 (Backend):
cd backend && source .venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 (Frontend):
cd frontend
npm run dev
```

### Verification

After setup, verify the application is running:

1. **Frontend**: http://localhost:3000 - Should see the login page
2. **Backend API**: http://localhost:8000/docs - Should see Swagger UI
3. **Chat Interface**: http://localhost:3000/chat - AI chat (after login)

---

## Environment Variables Quick Reference

### Backend (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (32+ chars) | `openssl rand -base64 32` |
| `GEMINI_API_KEY` | Yes | Google Gemini API key | Get from aistudio.google.com |
| `CORS_ORIGINS` | Yes | Allowed frontend origins | `http://localhost:3000` |
| `DEBUG` | No | Enable debug logging | `True` |

### Frontend (.env.local)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL | `http://localhost:8000` |
| `BETTER_AUTH_SECRET` | Yes | Must match backend secret | Same as backend |
| `NEXT_PUBLIC_DEBUG` | No | Enable debug mode | `true` |

---

## Chat Example Interactions

After logging in and navigating to `/chat`, try these interactions:

### 1. Adding a Task
```
You: "Add a task to buy groceries"
TaskBot: "Task added: 'Buy groceries'. What else can I help with?"
```

### 2. Listing Tasks
```
You: "Show me my tasks"
TaskBot: "Here are your tasks:
1. Buy groceries (pending)
2. Finish homework (pending)"
```

### 3. Completing a Task
```
You: "Mark 'buy groceries' as done"
TaskBot: "Great job! 'Buy groceries' is now complete."
```

### 4. Updating a Task
```
You: "Change 'Finish homework' to 'Finish math homework'"
TaskBot: "Task updated: 'Finish math homework'"
```

### 5. Deleting a Task
```
You: "Delete the 'Finish math homework' task"
TaskBot: "Task 'Finish math homework' has been deleted."
```

---

## Troubleshooting Quick Guide

### Issue: Frontend can't connect to backend
- Verify both servers are running
- Check `NEXT_PUBLIC_API_URL` in frontend/.env.local
- Check `CORS_ORIGINS` in backend/.env includes `http://localhost:3000`

### Issue: Authentication fails
- Ensure `BETTER_AUTH_SECRET` is identical in both .env files
- Restart both servers after changing secrets
- Clear browser cookies

### Issue: Database connection errors
- Verify PostgreSQL is accessible
- Check `DATABASE_URL` format: `postgresql+asyncpg://...`
- For Neon: ensure SSL is enabled in connection string

### Issue: Chat not responding
- Verify `GEMINI_API_KEY` is set in backend/.env
- Check backend logs for Gemini API errors
- Ensure you're logged in (auth required for chat)

### Issue: Rate limiting
- Gemini free tier: 5-15 requests per minute
- Wait and retry if you see rate limit errors
- Keep conversations focused to reduce API calls

---

## Version Requirements Summary

| Component | Minimum Version | Recommended |
|-----------|-----------------|-------------|
| Node.js | 18.x | 20.x LTS |
| npm | 10.x | Latest |
| Python | 3.10+ | 3.13+ |
| PostgreSQL | 14+ | Neon serverless |
| Next.js | 16.x | 16.0.10 |
| FastAPI | 0.115+ | 0.115.0 |
