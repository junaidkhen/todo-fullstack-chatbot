# Phase III Constitution - Todo AI Chatbot (Gemini Powered)

<!--
Sync Impact Report:
- Version: 1.0.0 (initial Phase III constitution)
- Added sections: All sections are new
- Templates requiring updates:
  - Plan template: Compatible (no changes needed)
  - Spec template: Compatible (no changes needed)
  - Tasks template: Compatible (no changes needed)
- Follow-up TODOs: None
-->

## 1. Project Objective

Build a stateless, AI-powered conversational Todo manager using natural language. Users can add, list, update, complete, and delete tasks via chat. State persists in Neon PostgreSQL ensuring server restarts do not lose conversations. Strictly Spec-Driven Development using Spec-Kit Plus + Claude Code. No manual code writing.

**Rationale**: Natural language interfaces reduce friction and enable faster task management. AI-powered chat provides intuitive, flexible interaction that adapts to user phrasing.

## Core Principles

### I. Spec-Driven Development Only

All development MUST be driven by specifications. No manual coding is permitted outside of the spec → plan → tasks → implementation workflow. Every feature begins with a complete specification that defines requirements, acceptance criteria, and constraints before any implementation work begins.

**Rationale**: Ensures clear requirements, prevents scope creep, enables better planning, and maintains full traceability from user intent to implementation.

### II. Stateless Backend Architecture

The backend MUST be stateless. No in-memory session storage is permitted. All conversation history and user state MUST be persisted in the database. Server restarts MUST NOT lose any user data or conversation context.

**Rationale**: Stateless architecture enables horizontal scaling, simplifies deployment, and ensures data durability. Users expect their conversation history to persist across sessions.

### III. Gemini API Free Tier Compliance

All AI operations MUST use Google Gemini API free tier only. No paid upgrade for hackathon scope. Model selection MUST support function calling (gemini-1.5-flash or gemini-2.5-flash). Rate limit awareness: keep context short, avoid unnecessary API calls.

**Rationale**: Hackathon budget constraints require free tier usage. Function calling support is essential for tool-based task management.

### IV. Friendly Conversational Interface

The AI MUST provide friendly, confirmatory responses in natural language. Mixed English/Urdu responses are acceptable. Error handling MUST use graceful, human-friendly messages (e.g., "Task nahi mila bhai" for task not found).

**Rationale**: User experience is paramount. Natural, friendly responses create engagement and reduce user frustration compared to technical error messages.

### V. Security Through User Isolation

User isolation MUST be enforced at all layers: database (user_id foreign keys), API (auth validation), and tool execution (ownership checks on every tool call). User data MUST never leak across user boundaries.

**Rationale**: Multi-user security is non-negotiable. Every tool call must validate that the user owns the resource being accessed.

### VI. Type Safety and Validation

All code MUST be fully typed:
- **Frontend**: TypeScript with strict mode enabled
- **Backend**: Python with type hints on all public functions and Pydantic models for all API contracts

All external inputs MUST be validated at system boundaries.

**Rationale**: Type safety catches errors at development time, improves code quality, and enables better tooling support.

### VII. Persistent Storage with Conversation History

All data MUST persist in Neon PostgreSQL. Database schema MUST include:
- `users` table managed by Better Auth
- `tasks` table with `user_id` foreign key enforcing referential integrity
- `conversations` table storing message history per user
- Proper indexes on frequently queried fields

**Rationale**: Conversation history enables context-aware AI responses. Users expect the AI to remember previous interactions within a session.

## Technology Stack Standards

### Frontend Requirements
- **Framework**: Custom Next.js chat UI (or Chainlit/Gradio if faster)
- **Language**: TypeScript with strict mode
- **Communication**: POST requests to backend /chat endpoint

### Backend Requirements
- **Framework**: FastAPI (single `/api/{user_id}/chat` endpoint)
- **AI SDK**: google-generativeai (Gemini SDK)
- **Model**: gemini-1.5-flash or gemini-2.5-flash (function calling support required)
- **ORM**: SQLModel for type-safe database interactions
- **Database**: Neon PostgreSQL (serverless Postgres)
- **Authentication**: Better Auth (user_id from auth)

### Environment Variables
- `GEMINI_API_KEY` - Google Gemini API key
- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT signing secret (shared with frontend)

### Explicitly NOT Included
- No OpenAI/ChatKit (switched to Gemini)
- No official MCP SDK (adapt to Gemini function calling schema)

## Architecture

### High-Level Flow

```
User → Chat UI → FastAPI /chat → Gemini Agent (function calling) → Tools execute DB ops → Response back
```

### Detailed Request Flow

1. **Receive user message**: Chat UI sends message to `/api/{user_id}/chat`
2. **Fetch conversation history**: Load recent messages from database
3. **Store user message**: Persist user input to conversation history
4. **Build Gemini prompt**: Combine history + system instructions + tool definitions
5. **Call Gemini**: Send prompt and receive function calls or text response
6. **Execute functions**: If function calls returned, execute DB operations
7. **Feed results back**: Send function results back to Gemini for final response
8. **Get final response**: Receive natural language response
9. **Store assistant message**: Persist AI response to conversation history
10. **Return to user**: Send response back to chat UI

## Tool Definitions (Gemini Function Calling Schema)

Five tools MUST be implemented:

### add_task
```
add_task(user_id: str, title: str, description: Optional[str])
```
Creates a new task for the user.

### list_tasks
```
list_tasks(user_id: str, status: Optional[str])
```
Lists user's tasks, optionally filtered by status (pending/completed).

### complete_task
```
complete_task(user_id: str, task_id: str)
```
Marks a task as completed.

### delete_task
```
delete_task(user_id: str, task_id: str)
```
Deletes a task (with ownership validation).

### update_task
```
update_task(user_id: str, task_id: str, title: Optional[str], description: Optional[str])
```
Updates task title and/or description.

## Non-Functional Requirements

### Context Window Management
- Keep context under 100k tokens
- Implement summarization if conversation history exceeds limits
- Prune oldest messages when approaching token limits

### Rate Limit Awareness
- Gemini free tier: 5-15 RPM (requests per minute)
- Design for low traffic patterns
- Implement graceful degradation on rate limit errors

### Security Requirements
- Validate user_id ownership on EVERY tool call
- No cross-user data access
- Audit logging for agent decisions

### Logging and Observability
- Log all agent decisions for debugging
- Track tool invocations and results
- Monitor API response times and error rates

## Project Structure

```
/
├── console/               # Phase I: In-memory console app (preserved)
├── frontend/              # Phase III: Chat UI
├── backend/               # Phase III: FastAPI + Gemini integration
├── specs/
│   ├── phase1/
│   │   └── constitution.md
│   ├── phase2/
│   │   └── constitution.md
│   └── phase3/
│       ├── constitution.md  # This file
│       └── [Phase III specifications]
├── history/
│   ├── prompts/           # Prompt History Records
│   └── adr/               # Architecture Decision Records
├── .specify/              # SpecKit Plus templates and scripts
├── CLAUDE.md              # Root agent instructions
├── frontend/CLAUDE.md     # Frontend-specific instructions
├── backend/CLAUDE.md      # Backend-specific instructions
└── README.md              # Setup, env, run commands
```

## Deliverables

### Backend (`/backend`)
- FastAPI application with `/api/{user_id}/chat` endpoint
- Gemini agent integration with function calling
- Tool implementations for all 5 task operations
- Conversation history persistence

### Frontend (`/frontend`)
- Chat UI (Next.js or Chainlit/Gradio)
- Message display and input
- User authentication integration

### Specifications (`/specs/phase3/`)
- This constitution
- Per-feature specifications
- API contract documentation

### Infrastructure
- Database migrations for conversation history
- Environment configuration templates
- README with setup and run instructions

## Phase Transition from Phase II

### Preserved from Phase II
- Neon PostgreSQL database
- SQLModel ORM
- Better Auth authentication
- User isolation principles
- Core 5 task operations

### New in Phase III
- **AI Chat Interface**: Natural language instead of forms/buttons
- **Gemini Integration**: AI-powered conversational agent
- **Function Calling**: Gemini native tool execution
- **Conversation History**: Persistent chat context
- **Single Endpoint**: `/api/{user_id}/chat` replaces REST CRUD endpoints

### Architectural Evolution
- **Interface**: Web forms → Chat UI
- **API Pattern**: REST CRUD → Single chat endpoint
- **Processing**: Direct CRUD → AI agent with function calling
- **Context**: Stateless requests → Conversation history

## Governance

### Constitution Authority
This Phase III constitution supersedes all other development practices for Phase III work. All specifications, plans, tasks, and implementations MUST comply with these principles. When conflicts arise, this document takes precedence.

### Amendment Process
Amendments to this constitution require:
1. Documented justification for the change
2. User approval of the proposed amendment
3. Version increment following semantic versioning:
   - **MAJOR**: Breaking changes to principles or removal of guarantees
   - **MINOR**: Addition of new principles or significant expansions
   - **PATCH**: Clarifications, wording improvements, non-semantic fixes
4. Update to all dependent templates and documentation
5. Communication of changes to all affected stakeholders

### Compliance and Review
- All pull requests MUST verify compliance with constitutional principles
- Complexity and deviation from standards MUST be justified with rationale
- Security requirements are non-negotiable and require explicit sign-off
- Rate limit compliance must be validated through testing

**Version**: 1.0.0 | **Ratified**: 2026-01-16 | **Last Amended**: 2026-01-16
