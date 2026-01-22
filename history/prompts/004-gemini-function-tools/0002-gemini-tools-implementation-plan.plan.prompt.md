---
id: 0002
title: Gemini Tools Implementation Plan
stage: plan
date: 2026-01-16
surface: agent
model: claude-opus-4-5-20251101
feature: 004-gemini-function-tools
branch: 010-deliverables-repo-structure
user: junaidkh84
command: /sp.plan
labels: ["gemini", "function-calling", "tools", "planning", "phase-3"]
links:
  spec: specs/004-gemini-function-tools/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-gemini-function-tools/plan.md
  - specs/004-gemini-function-tools/research.md
  - specs/004-gemini-function-tools/data-model.md
  - specs/004-gemini-function-tools/contracts/gemini-tools.json
  - specs/004-gemini-function-tools/quickstart.md
  - CLAUDE.md
tests:
  - N/A (planning phase - no code written)
---

## Prompt

chunk-3
You are strictly following the Constitution of Phase-III.

And this approved spec: [# Feature Specification: Gemini Function Calling Tools Definition

**Feature Branch**: `004-gemini-function-tools`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Chunk 3: Gemini Function Calling Tools Definition - Define the exact tool/function declarations that will be passed to Gemini model for native function calling"

## Overview

This specification defines the exact tool/function declarations that will be passed to the Gemini model for native function calling. These tools replace the original MCP tools concept and enable the AI chatbot to execute task management operations through natural language conversation.

The Gemini function calling schema uses a JSON-like format similar to OpenAI function calling, with specific adaptations for the google-generativeai SDK.

[... full spec content ...]

Generate IMPLEMENTATION PLAN for Chunk 3: Gemini Function Calling Tools Definition

Focus on declaring tools in Gemini SDK format (using dict / FunctionDeclaration style from google.generativeai).

Output:
# Chunk 3 Implementation Plan

1. Add google-generativeai to dependencies
2. Create a file e.g., backend/tools.py or backend/gemini_tools.py
3. Define a function that returns the list of tool declarations (dicts with name, description, parameters JSON schema)
4. Implement expected return JSON structures for each tool (success/error)
5. Write helper functions for tool execution (placeholders for DB ops, e.g., def add_task_impl(user_id, title, ...))
6. Test plan: Mock test that prints tool declarations and simulates a call
7. Notes on Gemini tool calling mode (auto / any / none if needed)

## Response snapshot

Created comprehensive implementation plan for Chunk 3: Gemini Function Calling Tools Definition.

**Key Decisions Made:**
1. **SDK Choice**: Use `google-genai` (unified SDK) instead of deprecated `google-generativeai`
2. **Declaration Style**: Use explicit `types.FunctionDeclaration` with `parameters_json_schema` for full control
3. **Execution Mode**: Manual function calling (disable automatic) to support async DB ops and ownership validation
4. **File Structure**: New `backend/src/gemini/tools.py` module for tool declarations

**Artifacts Generated:**
- `plan.md` - Full implementation plan with technical context and constitution check
- `research.md` - SDK research findings with 7 key decisions
- `data-model.md` - Tool entities and return type definitions
- `contracts/gemini-tools.json` - Complete JSON Schema for all 5 tools
- `quickstart.md` - Implementation guide with code examples and tests

**All 5 tools defined:**
1. `add_task` - Create new task (user_id, title, description?)
2. `list_tasks` - Retrieve tasks (user_id, status?)
3. `complete_task` - Mark done (user_id, task_id)
4. `delete_task` - Remove task (user_id, task_id)
5. `update_task` - Modify task (user_id, task_id, title?, description?)

## Outcome

- ✅ Impact: Phase 1 planning complete - all design artifacts generated for Chunk 3
- 🧪 Tests: No code written; unit test template provided in quickstart.md
- 📁 Files: 6 files created/modified (5 spec artifacts + CLAUDE.md context update)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks
- 🧠 Reflection: Researched current google-genai SDK via Context7 MCP - confirmed deprecated package replaced

## Evaluation notes (flywheel)

- Failure modes observed: None - spec was well-defined with clear tool schemas
- Graders run and results (PASS/FAIL): Constitution check PASS (all 7 principles validated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run tasks generation and validate against quickstart code
