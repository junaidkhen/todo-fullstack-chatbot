# Tasks: Deliverables & Final Repository Structure

**Input**: Design documents from `/specs/010-deliverables-repo-structure/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, quickstart.md
**Feature Type**: Documentation-only (no code changes)

**Tests**: Not applicable - this feature involves only documentation artifacts. Validation is manual.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify current repository state and prepare for documentation updates

- [X] T001 Verify project structure matches specs/010-deliverables-repo-structure/plan.md#project-structure
- [X] T002 [P] Confirm backend/requirements.txt exists and contains base dependencies
- [X] T003 [P] Confirm frontend/package.json exists and contains base dependencies
- [X] T004 [P] Confirm backend/.env.example exists with Phase II variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration files that MUST be complete before README documentation

**⚠️ CRITICAL**: No README updates can begin until environment templates are complete

- [X] T005 Add GEMINI_API_KEY to backend/.env.example with description comment
- [X] T006 [P] Add google-genai==0.5.0 to backend/requirements.txt with Phase III comment
- [X] T007 Verify frontend/.env.example contains all required variables (no changes expected)

**Checkpoint**: Environment configuration templates ready - README documentation can now begin

---

## Phase 3: User Story 1 - New Developer Onboarding (Priority: P1) 🎯 MVP

**Goal**: Enable new developers to get the application running locally within 15 minutes

**Independent Test**: Have someone unfamiliar with the project follow README instructions from scratch and verify the application runs successfully

### Implementation for User Story 1

- [X] T008 [US1] Write Prerequisites section in README.md with version requirements (Node.js 20.x+, Python 3.13+, PostgreSQL, Gemini API key)
- [X] T009 [US1] Write Quick Start section in README.md with 5 terminal commands per quickstart.md reference
- [X] T010 [US1] Write Environment Variables section in README.md - Backend variables table (DATABASE_URL, BETTER_AUTH_SECRET, GEMINI_API_KEY, CORS_ORIGINS, DEBUG)
- [X] T011 [US1] Write Environment Variables section in README.md - Frontend variables table (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_DEBUG)
- [X] T012 [US1] Write verification steps in README.md (frontend at :3000, backend at :8000/docs, chat at :3000/chat)

**Checkpoint**: At this point, a new developer can successfully set up and run the application following README alone

---

## Phase 4: User Story 2 - Project Maintainer Documentation Review (Priority: P2)

**Goal**: Enable maintainers to understand project structure and make informed decisions about feature placement

**Independent Test**: Ask a maintainer to identify where to place a new API endpoint or frontend component based solely on the documentation

### Implementation for User Story 2

- [X] T013 [US2] Write Project Structure section in README.md with tree diagram showing console/, frontend/, backend/, specs/, history/ directories
- [X] T014 [US2] Add directory descriptions explaining Phase I (console), Phase II/III (frontend/backend), specifications (specs/), and history (prompts/adr)
- [X] T015 [US2] Document file patterns in README.md (where to add API endpoints, React components, database models)

**Checkpoint**: At this point, a maintainer can identify correct locations for new code based on README structure documentation

---

## Phase 5: User Story 3 - Deployment Engineer Configuration (Priority: P3)

**Goal**: Provide complete environment configuration documentation for staging/production setup

**Independent Test**: Deploy to a fresh environment using only the documented configuration variables

### Implementation for User Story 3

- [X] T016 [US3] Document DATABASE_URL format and Neon PostgreSQL requirements in README.md environment section
- [X] T017 [P] [US3] Document BETTER_AUTH_SECRET requirements (32+ characters, shared between frontend/backend) in README.md
- [X] T018 [P] [US3] Document GEMINI_API_KEY acquisition steps in README.md (link to aistudio.google.com/apikey)
- [X] T019 [US3] Document CORS_ORIGINS configuration for production environments in README.md

**Checkpoint**: At this point, an engineer can configure the application for any environment using README documentation

---

## Phase 6: User Story 4 - Hackathon Judge Evaluation (Priority: P3)

**Goal**: Enable judges to quickly understand the project and test its functionality

**Independent Test**: Have an external evaluator assess the project based on README alone

### Implementation for User Story 4

- [X] T020 [US4] Write Overview section in README.md explaining project purpose (AI chatbot for task management)
- [X] T021 [US4] Write Features section in README.md listing Phase I (console), Phase II (web app), Phase III (AI chat) capabilities
- [X] T022 [US4] Write Chat Examples section in README.md with 5 example interactions (add, list, complete, update, delete) per quickstart.md reference
- [X] T023 [US4] Write API Endpoints section in README.md listing key endpoints (auth, tasks, chat)

**Checkpoint**: At this point, a judge can understand the project and test core functionality within 2 minutes

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Troubleshooting, edge cases, and final validation

- [X] T024 [P] Write Troubleshooting section in README.md - Connection issues (CORS, server not running)
- [X] T025 [P] Write Troubleshooting section in README.md - Authentication failures (mismatched secrets, cookie issues)
- [X] T026 [P] Write Troubleshooting section in README.md - Database errors (URL format, Neon SSL)
- [X] T027 [P] Write Troubleshooting section in README.md - AI chat issues (invalid API key, rate limiting)
- [X] T028 [P] Write Troubleshooting section in README.md - Port conflicts (3000, 8000 alternatives)
- [X] T029 Run end-to-end validation by following README.md instructions from clean state
- [X] T030 Verify all .env.example files match documented environment variables

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all README documentation
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (different README sections)
  - Or sequentially in priority order (P1 → P2 → P3 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3

### Within Each User Story

- Environment file updates before README documentation
- README sections can be written in any order within a story
- All tasks within a story should complete before marking story done

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- All Troubleshooting tasks in Phase 7 marked [P] can run in parallel

---

## Parallel Example: Phase 7 (Troubleshooting)

```bash
# Launch all troubleshooting tasks together:
Task: "Write Troubleshooting section - Connection issues in README.md"
Task: "Write Troubleshooting section - Authentication failures in README.md"
Task: "Write Troubleshooting section - Database errors in README.md"
Task: "Write Troubleshooting section - AI chat issues in README.md"
Task: "Write Troubleshooting section - Port conflicts in README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verification)
2. Complete Phase 2: Foundational (environment templates)
3. Complete Phase 3: User Story 1 (onboarding documentation)
4. **STOP and VALIDATE**: Follow README from scratch
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Templates ready
2. Add User Story 1 → Test onboarding → Functional setup docs (MVP!)
3. Add User Story 2 → Test structure understanding → Structure docs complete
4. Add User Story 3 → Test deployment config → Config docs complete
5. Add User Story 4 → Test judge evaluation → Full documentation
6. Add Polish → Troubleshooting complete → Final deliverable

### Full Implementation (Single Developer)

1. Phase 1: ~5 minutes (verification tasks)
2. Phase 2: ~5 minutes (environment template updates)
3. Phase 3-6: ~30-45 minutes (README sections)
4. Phase 7: ~15 minutes (troubleshooting + validation)

---

## Notes

- [P] tasks = different files or README sections, no dependencies
- [Story] label maps task to specific user story for traceability
- This feature is documentation-only - no code implementation
- All README content references are in quickstart.md, research.md
- Validate by following README instructions from clean clone
- Commit after each phase completion

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 30 |
| Setup Tasks | 4 |
| Foundational Tasks | 3 |
| US1 Tasks | 5 |
| US2 Tasks | 3 |
| US3 Tasks | 4 |
| US4 Tasks | 4 |
| Polish Tasks | 7 |
| Parallel Opportunities | 15 tasks marked [P] |
| MVP Scope | T001-T012 (Phases 1-3) |

**Generated**: 2026-01-17 | **Status**: Ready for Implementation
