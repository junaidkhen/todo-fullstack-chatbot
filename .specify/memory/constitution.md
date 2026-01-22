# Todo Application Constitution - Multi-Phase Governance

<!--
Sync Impact Report:
- Version change: 2.0.0 → 3.0.0
- Modified principles: None (routing document only)
- Added sections: Phase III routing entry, Phase III Constitution Summary
- Removed sections: None
- Templates requiring updates:
  ✅ Plan template compatibility verified
  ✅ Spec template compatibility verified
  ✅ Tasks template compatibility verified
- Follow-up TODOs: None
-->

## Overview

This project uses **phase-specific constitutions** to govern different architectural stages of the Todo application. Each phase has its own constitution that defines principles, constraints, and standards appropriate to that phase's architecture.

## Constitution Routing

The active constitution depends on which phase you're working on:

| Phase | Constitution File | Status | Architecture |
|-------|------------------|--------|--------------|
| **Phase I** | [`specs/phase1/constitution.md`](../../specs/phase1/constitution.md) | ✅ **Completed** | In-memory console app |
| **Phase II** | [`specs/phase2/constitution.md`](../../specs/phase2/constitution.md) | ✅ **Completed** | Full-stack web app |
| **Phase III** | [`specs/phase3/constitution.md`](../../specs/phase3/constitution.md) | 🚧 **Active** | AI Chatbot (Gemini Powered) |

### How to Use

1. **Working on Phase I** (console app maintenance):
   - Follow `specs/phase1/constitution.md`
   - Applies to code in `/console` directory
   - Principles: TDD, in-memory storage, CLI interface

2. **Working on Phase II** (full-stack web app maintenance):
   - Follow `specs/phase2/constitution.md`
   - Applies to code in `/frontend` and `/backend` directories
   - Principles: Multi-user, persistence, REST API, JWT auth

3. **Working on Phase III** (AI chatbot - current focus):
   - Follow `specs/phase3/constitution.md`
   - Applies to Gemini integration and chat UI
   - Principles: Stateless backend, Gemini free tier, conversational interface

4. **Working on shared infrastructure** (this is rare):
   - Follow universal principles (listed below)
   - Applies to root-level configuration files

## Universal Principles (All Phases)

These principles apply to **all phases** of the project:

### I. Spec-Driven Development

All development MUST follow the spec → plan → tasks → implementation workflow. No manual coding outside this workflow. Every feature begins with a complete specification.

### II. Type Safety

All code MUST be fully typed according to the language:
- **Python**: Type hints on all public functions
- **TypeScript**: Strict mode enabled

### III. Clean Architecture

Maintain clear separation of concerns with well-defined module boundaries. Dependencies flow in one direction. Each layer has a single responsibility.

### IV. Quality Standards

- Clear, meaningful error messages
- Comprehensive input validation
- No hardcoded secrets (use `.env`)
- Code follows language-specific style guides (PEP 8 for Python, ESLint for TypeScript)

### V. Documentation

- All specifications under `/specs/`
- Prompt history records under `/history/prompts/`
- Architecture Decision Records under `/history/adr/`
- README files at appropriate levels

## Phase-Specific Governance

Each phase constitution is authoritative for its domain. When conflicts arise between universal principles and phase-specific principles, the **phase-specific constitution takes precedence** for code within that phase's directory.

### Phase I Constitution Summary

**File**: `specs/phase1/constitution.md`

**Core Principles**:
1. Simplicity First (no external dependencies)
2. Type Safety (Python type hints)
3. Test-Driven Development (Red-Green-Refactor)
4. Input Validation and Error Handling
5. In-Memory Storage Only
6. Command-Line Interface (REPL)
7. Clean Architecture

**Applies To**: `/console` directory (formerly `Todo-app/`)

### Phase II Constitution Summary

**File**: `specs/phase2/constitution.md`

**Core Principles**:
1. Spec-Driven Development Only
2. Multi-User Isolation and Security
3. Clean Architecture and Separation of Concerns
4. Stateless JWT Authentication
5. Type Safety and Validation
6. Persistent Storage with Clear Schema
7. RESTful API Design

**Applies To**: `/frontend` and `/backend` directories (REST API mode)

### Phase III Constitution Summary

**File**: `specs/phase3/constitution.md`

**Core Principles**:
1. Spec-Driven Development Only
2. Stateless Backend Architecture
3. Gemini API Free Tier Compliance
4. Friendly Conversational Interface
5. Security Through User Isolation
6. Type Safety and Validation
7. Persistent Storage with Conversation History

**Applies To**: `/frontend` (chat UI) and `/backend` (Gemini integration)

**Technology Stack**:
- AI: Google Gemini API (free tier) with function calling
- Model: gemini-1.5-flash or gemini-2.5-flash
- Backend: FastAPI single `/api/{user_id}/chat` endpoint
- ORM/DB: SQLModel + Neon PostgreSQL
- Auth: Better Auth (user_id from auth)

## Monorepo Structure

```
/
├── console/                        # Phase I: In-memory console app
│   └── [Governed by specs/phase1/constitution.md]
├── frontend/                       # Phase II/III: Next.js web app / Chat UI
│   └── [Governed by specs/phase3/constitution.md - current]
├── backend/                        # Phase II/III: FastAPI backend / Gemini integration
│   └── [Governed by specs/phase3/constitution.md - current]
├── specs/
│   ├── phase1/
│   │   ├── constitution.md         # Phase I governance
│   │   └── [Phase I specifications]
│   ├── phase2/
│   │   ├── constitution.md         # Phase II governance
│   │   └── [Phase II specifications]
│   └── phase3/
│       ├── constitution.md         # Phase III governance
│       └── [Phase III specifications]
├── history/
│   ├── prompts/                    # Prompt History Records
│   └── adr/                        # Architecture Decision Records
├── .specify/
│   ├── memory/
│   │   └── constitution.md         # This file (routing document)
│   ├── templates/                  # Spec, plan, tasks templates
│   └── scripts/                    # Helper scripts
├── CLAUDE.md                       # Root agent instructions
├── frontend/CLAUDE.md              # Frontend agent instructions
└── backend/CLAUDE.md               # Backend agent instructions
```

## Amendment Process

### Amending a Phase-Specific Constitution

To amend a phase constitution (e.g., `specs/phase3/constitution.md`):

1. Document justification for the change
2. Get user approval
3. Increment version following semantic versioning:
   - **MAJOR**: Breaking changes to principles
   - **MINOR**: New principles or significant expansions
   - **PATCH**: Clarifications, wording fixes
4. Update dependent templates and documentation
5. Update this routing document if governance structure changes

### Amending Universal Principles

To amend the universal principles in this file:

1. Ensure change doesn't conflict with phase-specific constitutions
2. Document justification
3. Get user approval
4. Increment this file's version
5. Notify all phases of the change

## Compliance and Review

### For Phase I (Console App)
- Follow `specs/phase1/constitution.md`
- PEP 8 compliance required
- TDD workflow enforced
- 80% minimum test coverage

### For Phase II (Full-Stack Web - REST Mode)
- Follow `specs/phase2/constitution.md`
- Security review required for auth/authorization changes
- Multi-user isolation verified on all data operations
- Type safety enforced (TypeScript strict mode, Python type hints)

### For Phase III (AI Chatbot - Current)
- Follow `specs/phase3/constitution.md`
- Gemini API free tier compliance required
- Rate limit awareness (5-15 RPM)
- User isolation on all tool calls
- Conversation history persistence verified

### For All Phases
- All PRs verify constitutional compliance
- Complexity must be justified
- Specifications required before implementation
- Prompt History Records created for all work

## Version History

| Version | Date | Change Summary |
|---------|------|----------------|
| 1.0.0 | 2026-01-02 | Initial unified constitution for Phase II |
| 2.0.0 | 2026-01-02 | **MAJOR**: Restructured into phase-specific constitutions with routing |
| 3.0.0 | 2026-01-16 | **MAJOR**: Added Phase III (AI Chatbot with Gemini) constitution |

**Current Version**: 3.0.0 | **Last Amended**: 2026-01-16
