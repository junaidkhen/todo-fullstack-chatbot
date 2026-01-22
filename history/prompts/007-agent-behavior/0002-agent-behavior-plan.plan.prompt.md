---
id: "0002"
title: Agent Behavior Implementation Plan
stage: plan
date: 2026-01-17
surface: agent
model: claude-opus-4-5-20251101
feature: 007-agent-behavior
branch: 007-agent-behavior
user: junaid
command: /sp.plan
labels: ["prompt-engineering", "system-prompt", "intent-mapping", "agent-behavior"]
links:
  spec: specs/007-agent-behavior/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-agent-behavior/plan.md
  - specs/007-agent-behavior/research.md
  - specs/007-agent-behavior/data-model.md
  - specs/007-agent-behavior/contracts/system-prompt.md
  - specs/007-agent-behavior/quickstart.md
  - CLAUDE.md
tests:
  - (none - planning phase)
---

## Prompt

chunk-6
You are strictly following the Constitution of Phase-III

And spec: [# Feature Specification: Agent Behavior & Natural Language Understanding Rules (Chunk 6)

**Feature Branch**: `007-agent-behavior`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Chunk 6: Agent Behavior & Natural Language Understanding Rules - Define agent instructions, intent-to-tool mapping, confirmation rules, error handling, multi-step logic."

## Overview

This specification defines the behavioral rules, natural language understanding patterns, and conversational guidelines for the Gemini AI agent. It extends the system prompt from Chunk 5 with detailed instructions for:

1. Intent recognition and mapping to tool calls
2. Confirmation and acknowledgment patterns
3. Multi-step reasoning for ambiguous requests
4. Error handling with friendly, localized messages
5. Tone and language adaptation (English/Urdu mixing)
6. Disambiguation strategies for unclear user input
...

Generate PLAN for Chunk 6: Agent Behavior & Intent Mapping

(This is mostly prompt engineering + rules in system prompt)

Output:
# Chunk 6 Implementation Plan

1. Refine system prompt text (intent mapping table as bullet points)
2. Add confirmation / error handling rules
3. Integrate updated prompt into agent init (Chunk 5)
4. Test: Send sample user messages → verify tool choice

## Response snapshot

Created implementation plan for Chunk 6 (Agent Behavior & NLU Rules):

**Deliverables Created:**
1. `specs/007-agent-behavior/plan.md` - Full implementation plan with:
   - Technical Context (Python 3.12, prompt engineering focus)
   - Constitution Check (all gates passed)
   - Project structure documentation
   - Implementation sequence

2. `specs/007-agent-behavior/research.md` - Phase 0 research covering:
   - Gemini system prompt best practices
   - Intent recognition patterns for task management
   - Urdu/English code-switching patterns
   - Multi-step reasoning instruction techniques
   - Error message design principles

3. `specs/007-agent-behavior/data-model.md` - Conceptual entities:
   - SYSTEM_PROMPT structure
   - Intent types and tool mappings
   - TaskReference resolution flow
   - Confirmation and Error templates

4. `specs/007-agent-behavior/contracts/system-prompt.md` - Complete system prompt (~1050 tokens):
   - TaskBot persona and personality
   - Conversation rules (6 sections)
   - Intent recognition examples
   - Error message templates with Urdu phrases
   - Constraints section

5. `specs/007-agent-behavior/quickstart.md` - Implementation guide:
   - Step-by-step integration instructions
   - Code snippets for prompts.py and agent.py
   - Testing checklist
   - Common issues and solutions

6. Updated `CLAUDE.md` with 007-agent-behavior context

## Outcome

- ✅ Impact: Created complete planning artifacts for Chunk 6 agent behavior implementation
- 🧪 Tests: No tests run (planning phase); manual testing checklist documented in quickstart.md
- 📁 Files: 6 files created/modified (plan.md, research.md, data-model.md, system-prompt.md, quickstart.md, CLAUDE.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks; implement system prompt constant
- 🧠 Reflection: This chunk is primarily prompt engineering rather than code - the main deliverable is the SYSTEM_PROMPT constant text

## Evaluation notes (flywheel)

- Failure modes observed: None - planning phase completed successfully
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test system prompt with sample messages after implementation
