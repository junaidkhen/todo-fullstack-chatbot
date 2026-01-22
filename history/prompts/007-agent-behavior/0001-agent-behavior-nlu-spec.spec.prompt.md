---
id: "0001"
title: "Agent Behavior NLU Spec"
stage: spec
date: 2026-01-16
surface: agent
model: claude-opus-4-5-20251101
feature: 007-agent-behavior
branch: 007-agent-behavior
user: junaidkh84
command: /sp.specify
labels: ["chunk-6", "agent-behavior", "nlu", "system-prompt", "intent-mapping"]
links:
  spec: specs/007-agent-behavior/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-agent-behavior/spec.md
  - specs/007-agent-behavior/checklists/requirements.md
tests:
  - N/A (specification phase)
---

## Prompt

chunk-6
You are strictly following this Constitution: [# Phase III Constitution - Todo AI Chatbot (Gemini Powered)...]

Generate SPEC for "Chunk 6: Agent Behavior & Natural Language Understanding Rules"

Objective: Define agent instructions, intent-to-tool mapping, confirmation rules, error handling, multi-step logic.

Output Format:
# Chunk 6 Spec: Agent Behavior Rules

## System Prompt Additions (append to Chunk 5 prompt)
- Always reply in friendly tone (English/Urdu mix if user uses)
- Confirm every action: "Done! Task added: ..."
- If ambiguous → ask clarification or use list_tasks first

## Intent Mapping Table
User says...               → Tool(s)
"add task buy milk"        → add_task
"show pending tasks"       → list_tasks(status="pending")
"mark task 3 done"         → complete_task
"delete the old task"      → list_tasks → delete_task (multi-turn)
...

## Multi-step Reasoning Rules
- If user says "delete the meeting" → call list_tasks first, then in next agent turn delete if clear
- Error cases: "Task not found" → "Sorry bhai, task ID galat lag raha hai"

## Tone & Language
...

## Response snapshot

Created comprehensive specification for Chunk 6: Agent Behavior & Natural Language Understanding Rules including:

1. **System Prompt Enhancements**: Complete behavioral instructions for TaskBot persona with English/Urdu code-switching, confirmation patterns, and error handling guidelines.

2. **Intent Mapping Table**: 19 user phrase patterns mapped to corresponding tool calls (ADD, LIST, COMPLETE, DELETE, UPDATE, GREETING, HELP, ACKNOWLEDGMENT).

3. **Multi-Step Reasoning Rules**: 4 rules covering name-based task resolution, pronoun resolution, sequential operations, and pre-action validation.

4. **Confirmation Templates**: Success confirmations for all 5 operations plus empty state responses.

5. **Error Message Templates**: 8 friendly, localized error messages in English/Urdu style.

6. **7 User Stories** with acceptance scenarios covering direct task creation, filtered listing, ambiguous references, completion, updates, error handling, and conversational greetings.

7. **12 Functional Requirements** and **8 Success Criteria** that are measurable and technology-agnostic.

## Outcome

- ✅ Impact: High - Defines agent personality and NLU patterns for consistent UX
- 🧪 Tests: N/A (specification phase)
- 📁 Files: 2 created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: /sp.plan for implementation planning
- 🧠 Reflection: Spec extends Chunk 5 agent runner with behavioral rules; no clarifications needed as all patterns derived from Phase III constitution

## Evaluation notes (flywheel)

- Failure modes observed: None - spec complete and validates against checklist
- Graders run and results (PASS/FAIL): All checklist items PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
