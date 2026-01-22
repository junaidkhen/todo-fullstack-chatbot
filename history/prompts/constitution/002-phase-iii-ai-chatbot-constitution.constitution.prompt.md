---
id: 002
title: Phase III AI Chatbot Constitution
stage: constitution
date: 2026-01-16
surface: agent
model: claude-opus-4-5-20251101
feature: phase3-ai-chatbot
branch: main
user: junaid
command: /sp.constitution
labels: ["phase3", "gemini", "ai-chatbot", "constitution"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/phase3/constitution.md
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

update the old contitution file with this one
# Project Constitution: Phase III - Todo AI Chatbot (Gemini Powered)

## 1. Project Objective
Build a stateless, AI-powered conversational Todo manager using natural language.
Users can add, list, update, complete, delete tasks via chat.
State persists in Neon PostgreSQL — server restarts don't lose conversations.
Strictly Spec-Driven Development using Spec-Kit Plus + Claude Code. No manual code writing.

## 2. Core Principles
- Spec-Driven only: All code generated/refined via Claude Code from specs.
- Stateless backend: No in-memory session; everything from DB.
- Gemini API free tier only (no paid upgrade for hackathon).
- Friendly, confirmatory responses in natural language (English/Urdu mix possible).
- Error handling: Graceful messages (e.g., "Task nahi mila bhai").
- Rate limit awareness: Keep context short, avoid unnecessary calls.

## 3. Technology Stack
- Frontend: Custom Next.js chat UI (or Chainlit/Gradio if faster) — POST to backend.
- Backend: Python FastAPI (single /api/{user_id}/chat endpoint).
- AI: Google Gemini API (free tier) + google-generativeai SDK.
  - Model: gemini-1.5-flash or gemini-2.5-flash (tool calling support wala).
- Tools/Function Calling: Gemini native function calling (no official MCP SDK — adapt to Gemini schema).
- ORM/DB: SQLModel + Neon Serverless PostgreSQL.
- Auth: Better Auth (user_id from auth).
- Env Vars:
  - GEMINI_API_KEY
  - DATABASE_URL
- No OpenAI/ChatKit (switched to Gemini).

## 4. Architecture
User → Chat UI → FastAPI /chat → Gemini Agent (with function calling) → Tools execute DB ops → Response back.

Flow:
1. Receive user message.
2. Fetch conversation history from DB.
3. Store user message.
4. Build Gemini prompt (history + system instructions + tools).
5. Call Gemini → get function calls or text.
6. If functions: Execute (DB ops), feed results back to Gemini.
7. Get final response.
8. Store assistant message.
9. Return to user.

## 5. Tools (Gemini Function Calling Schema)
5 tools:
- add_task(user_id, title, description?)
- list_tasks(user_id, status?)
- complete_task(user_id, task_id)
- delete_task(user_id, task_id)
- update_task(user_id, task_id, title?, description?)

## 6. Non-Functional
- Context window: Keep under 100k tokens (summarize if long).
- Rate limits: 5-15 RPM free tier → design for low traffic.
- Security: Validate user_id ownership on every tool call.
- Logging: Agent decisions log for debug.

## 7. Deliverables
- /backend: FastAPI + Gemini integration
- /frontend: Chat UI
- /specs: Constitution + per-chunk specs
- Migrations
- README: Setup, env, run commands

## Response snapshot

Created Phase III constitution for AI Chatbot with Gemini integration:

1. **Created**: `specs/phase3/constitution.md` (v1.0.0)
   - 7 core principles: Spec-Driven Development, Stateless Backend, Gemini Free Tier Compliance, Friendly Conversational Interface, Security Through User Isolation, Type Safety, Persistent Storage with Conversation History
   - Technology stack: Gemini API, FastAPI single chat endpoint, SQLModel + Neon PostgreSQL, Better Auth
   - 5 tools defined: add_task, list_tasks, complete_task, delete_task, update_task
   - Detailed architecture flow with 10 steps
   - Non-functional requirements: rate limits, context window management, security, logging

2. **Updated**: `.specify/memory/constitution.md` (v2.0.0 → v3.0.0)
   - Added Phase III routing entry with 🚧 Active status
   - Added Phase III Constitution Summary section
   - Updated monorepo structure documentation
   - Added Phase III compliance requirements

## Outcome

- ✅ Impact: Major version bump (3.0.0) - new phase constitution added
- 🧪 Tests: N/A (documentation only)
- 📁 Files: 2 files created/modified (specs/phase3/constitution.md, .specify/memory/constitution.md)
- 🔁 Next prompts: Create feature specs for Phase III implementation, run /sp.specify for chat feature
- 🧠 Reflection: Constitution successfully captures Gemini-specific constraints (free tier, rate limits) and conversational interface requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution against actual Gemini API capabilities during implementation
