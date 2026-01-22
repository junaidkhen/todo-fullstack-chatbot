# Research: Deliverables & Final Repository Structure

**Feature Branch**: `010-deliverables-repo-structure`
**Created**: 2026-01-17
**Status**: Complete

## Research Summary

This research phase analyzed the current repository state and identified gaps between the existing documentation and the Phase III AI chatbot requirements.

---

## 1. Current Project Structure Audit

### Decision: Multi-phase monorepo structure is correctly organized

**Findings**:
- Repository follows monorepo pattern with `console/`, `frontend/`, `backend/`, `specs/` directories
- Phase I console app preserved in `/console`
- Phase II/III share `/frontend` and `/backend` directories
- Specifications organized by feature number (001-010)

**Current Structure**:
```
todo-fullstack/
├── console/              # Phase I: In-memory console app
├── frontend/             # Phase II/III: Next.js web app + Chat UI
│   ├── src/
│   │   ├── app/         # App Router pages (signup, signin, tasks)
│   │   ├── components/  # React components (TaskList, TaskForm, etc.)
│   │   └── lib/         # Utilities (auth, api)
│   ├── package.json
│   └── .env.example
├── backend/              # Phase II/III: FastAPI backend + Gemini integration
│   ├── src/
│   │   ├── models/      # SQLModel database models
│   │   ├── api/         # FastAPI route handlers
│   │   ├── auth/        # JWT validation logic
│   │   └── database.py  # Database connection management
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── specs/                # Feature specifications
│   ├── phase1/          # Phase I constitution
│   ├── phase2/          # Phase II constitution
│   ├── phase3/          # Phase III constitution
│   └── ###-feature/     # Per-feature specs
├── history/
│   ├── prompts/         # Prompt History Records
│   └── adr/             # Architecture Decision Records
├── .specify/            # SpecKit Plus templates and scripts
├── CLAUDE.md            # Agent instructions
└── README.md            # Main documentation
```

**Alternatives Considered**:
- Separate repositories per phase: Rejected due to shared authentication and database

---

## 2. README.md Gap Analysis

### Decision: README must be updated for Phase III

**Current README Coverage**:
| Section | Phase II | Phase III | Gap |
|---------|----------|-----------|-----|
| Quick Start | ✅ Complete | ❌ Missing | Need chat-specific setup |
| Prerequisites | ✅ Complete | ⚠️ Partial | Missing Gemini API key |
| Environment Variables | ✅ Complete | ❌ Missing | Missing GEMINI_API_KEY |
| Project Structure | ✅ Complete | ⚠️ Partial | Need to add chat components |
| Example Interactions | ❌ N/A | ❌ Missing | Need 5 core operations |
| Troubleshooting | ✅ 4 issues | ❌ Missing | Need AI-specific issues |

**Required Updates**:
1. Add GEMINI_API_KEY to environment variables section
2. Add chat example interactions demonstrating 5 operations
3. Add AI chat troubleshooting (API key invalid, rate limiting)
4. Update project structure to reflect Phase III components
5. Add "Features" section with AI chatbot description

---

## 3. Environment Variables Completeness

### Decision: Update .env.example files for Phase III

**Backend .env.example Current**:
```
DATABASE_URL=postgresql+asyncpg://...
BETTER_AUTH_SECRET=...
DEBUG=True
```

**Backend .env.example Required**:
```
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@host:5432/todo_db

# Authentication Secret (shared with frontend)
BETTER_AUTH_SECRET=<32-char-secret>

# AI Configuration (Phase III)
GEMINI_API_KEY=<your-gemini-api-key>

# Development settings
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

**Frontend .env.example Current**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=...
NEXT_PUBLIC_DEBUG=true
```

**Frontend .env.example Required** (no changes needed - chat uses same API URL):
- No additional variables required for Phase III

---

## 4. Dependency Files Status

### Decision: requirements.txt needs google-genai dependency

**Current backend/requirements.txt**:
- fastapi==0.115.0
- sqlmodel==0.0.22
- asyncpg==0.30.0
- pyjwt==2.9.0
- uvicorn==0.32.0
- pytest==8.3.4

**Required Addition**:
```
# AI Integration (Phase III)
google-genai==0.5.0
```

**Frontend package.json**: ✅ Complete (no AI-specific dependencies needed)

---

## 5. Chat Example Interactions

### Decision: Document 5 core operations with natural language examples

**Research on Effective Chat Examples**:
Based on Phase III constitution's "Friendly Conversational Interface" principle, examples should show:
1. Natural language input
2. Expected AI response format
3. Mixed English/Urdu where appropriate

**Proposed Examples**:

```markdown
### Adding a Task
User: "Add a task to buy groceries"
TaskBot: "✅ Task added: 'Buy groceries'. What else can I help with?"

### Listing Tasks
User: "Show me my pending tasks"
TaskBot: "📋 Here are your pending tasks:
1. Buy groceries
2. Finish homework
3. Call mom"

### Completing a Task
User: "Mark 'buy groceries' as done"
TaskBot: "✅ Great job! I've marked 'Buy groceries' as completed."

### Updating a Task
User: "Change 'Finish homework' to 'Finish math homework'"
TaskBot: "✅ Task updated: 'Finish math homework'"

### Deleting a Task
User: "Delete the 'Call mom' task"
TaskBot: "🗑️ Task 'Call mom' has been deleted."
```

---

## 6. Troubleshooting Section Analysis

### Decision: Add 3+ AI-specific troubleshooting items

**Current Troubleshooting** (Phase II):
1. Frontend can't connect to backend
2. Authentication fails between frontend and backend
3. Database connection errors
4. Task data not persisting

**Required Phase III Additions**:
1. **Gemini API key invalid**
   - Symptom: Chat returns "AI service unavailable" error
   - Solution: Verify GEMINI_API_KEY in backend/.env
   - How to get key: Visit https://aistudio.google.com/apikey

2. **Rate limiting errors**
   - Symptom: "Rate limit exceeded" responses
   - Solution: Free tier allows 5-15 RPM; wait and retry

3. **Chat not responding**
   - Symptom: No AI response after sending message
   - Solution: Check backend logs for Gemini API errors

---

## 7. Prerequisites and Version Requirements

### Decision: Document all version requirements

**Verified Prerequisites**:

| Dependency | Required Version | Source |
|------------|------------------|--------|
| Node.js | 20.x+ | frontend/package.json |
| npm | 10.x+ | Node.js LTS bundled |
| Python | 3.13+ | README.md current |
| PostgreSQL | 15+ | Neon serverless |
| Git | 2.x+ | Standard |

**Version Justification**:
- Node.js 20.x: Next.js 16 compatibility
- Python 3.13: FastAPI async support
- PostgreSQL 15: Neon serverless compatibility

---

## 8. .gitignore Completeness

### Decision: Current .gitignore is comprehensive, no changes needed

**Current Coverage**:
- ✅ Python artifacts (__pycache__, *.pyc, .eggs/)
- ✅ Virtual environments (.venv/, venv/)
- ✅ Environment files (.env, .env.*, !.env.example)
- ✅ IDE files (.vscode/, .idea/)
- ✅ Testing artifacts (.pytest_cache/, .coverage)
- ✅ OS files (.DS_Store, Thumbs.db)
- ✅ Node modules (in frontend/.gitignore)

No additional patterns required.

---

## Resolved NEEDS CLARIFICATION Items

| Item | Resolution |
|------|------------|
| Phase III components location | Chat UI in frontend/src/app/chat/, Gemini in backend/src/api/chat.py |
| GEMINI_API_KEY required | Yes, required for Phase III functionality |
| Example format | Natural language with emoji confirmations |
| Troubleshooting scope | 3 minimum AI-specific issues required |

---

## Next Steps

1. **Phase 1 Planning**: Create data-model.md, contracts/, quickstart.md
2. **Implementation**: Update README.md, .env.example files, requirements.txt
3. **Validation**: Test end-to-end setup following documented instructions
