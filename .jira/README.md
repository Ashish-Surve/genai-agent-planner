# ADHD Planner - Implementation Stories

## Overview

This folder contains implementation stories broken down into manageable chunks that can be completed within Claude's 4-hour session limits. Each story is self-contained and includes clear acceptance criteria.

## Story Structure

Each story follows this format:
- **Story ID**: Unique identifier
- **Title**: Clear, concise description
- **Epic**: Which feature area it belongs to
- **Estimated Time**: < 4 hours
- **Prerequisites**: What must be completed first
- **Description**: Detailed context
- **Acceptance Criteria**: Clear definition of done
- **Files to Create/Modify**: Specific file list
- **Implementation Notes**: Helpful tips and patterns
- **Testing Checklist**: How to verify it works

## Implementation Order

Stories must be completed in order as each builds on previous work.

### Epic 1: Foundation (Stories 1-5)
Foundation layer - database, models, configuration.

| Story | Title | Time | Status |
|-------|-------|------|--------|
| ADHD-1 | Project Setup & Configuration | 2h | ✅ Complete |
| ADHD-2 | Database Schema & Migrations | 3h | ✅ Complete |
| ADHD-3 | Pydantic Models & Enums | 2h | ✅ Complete |
| ADHD-4 | Base Repository Pattern | 2h | ✅ Complete |
| ADHD-5 | Task & TimeBlock Repositories | 3h | ✅ Complete |

**Total: ~12 hours** (3 sessions)

### Epic 2: Core Services (Stories 6-10)
Business logic and service layer.

| Story | Title | Time | Status |
|-------|-------|------|--------|
| ADHD-6 | Configuration & Logging | 2h | ✅ Complete |
| ADHD-7 | LLM Service & Provider Factory | 3h | ✅ Complete |
| ADHD-8 | Task Service | 3h | ✅ Complete |
| ADHD-9 | Calendar Service | 3h | ✅ Complete |
| ADHD-10 | Time Estimation Service | 2h | ✅ Complete |

**Total: ~13 hours** (4 sessions)

### Epic 3: LangGraph Agents (Stories 11-16)
AI agent system with LangGraph.

| Story | Title | Time | Status |
|-------|-------|------|--------|
| ADHD-11 | LangGraph State & Base Agent | 3h | 📋 Not Started |
| ADHD-12 | Supervisor Agent | 3h | 📋 Not Started |
| ADHD-13 | Planning Agent | 3h | 📋 Not Started |
| ADHD-14 | Scheduling Agent | 4h | 📋 Not Started |
| ADHD-15 | Suggestion Agent | 2h | 📋 Not Started |
| ADHD-16 | Graph Builder & Integration | 3h | 📋 Not Started |

**Total: ~18 hours** (5 sessions)

### Epic 4: Streamlit UI (Stories 17-21)
User interface with Streamlit.

| Story | Title | Time | Status |
|-------|-------|------|--------|
| ADHD-17 | Streamlit App Structure | 2h | 📋 Not Started |
| ADHD-18 | Chat Page & Components | 3h | 📋 Not Started |
| ADHD-19 | Tasks Page & Components | 3h | 📋 Not Started |
| ADHD-20 | Calendar View | 4h | 📋 Not Started |
| ADHD-21 | Settings Page | 2h | 📋 Not Started |

**Total: ~14 hours** (4 sessions)

### Epic 5: Apple Integration (Stories 22-25)
macOS integration with Reminders and Calendar.

| Story | Title | Time | Status |
|-------|-------|------|--------|
| ADHD-22 | Apple Permissions & Setup | 2h | 📋 Not Started |
| ADHD-23 | Reminders Integration | 3h | 📋 Not Started |
| ADHD-24 | Calendar Integration | 3h | 📋 Not Started |
| ADHD-25 | Sync Service & Conflict Resolution | 4h | 📋 Not Started |

**Total: ~12 hours** (3 sessions)

### Epic 6: ADHD Features (Stories 26-29)
ADHD-specific intelligence features.

| Story | Title | Time | Status |
|-------|-------|------|--------|
| ADHD-26 | Energy Service & Logging | 2h | 📋 Not Started |
| ADHD-27 | Energy Agent & Pattern Analysis | 3h | 📋 Not Started |
| ADHD-28 | Sync Agent | 2h | 📋 Not Started |
| ADHD-29 | Buffer Time & Context Switching | 2h | 📋 Not Started |

**Total: ~9 hours** (3 sessions)

### Epic 7: Polish & Testing (Stories 30-33)
Error handling, testing, and final integration.

| Story | Title | Time | Status |
|-------|-------|------|--------|
| ADHD-30 | Error Handling & Logging | 2h | 📋 Not Started |
| ADHD-31 | Unit Tests - Core Services | 3h | 📋 Not Started |
| ADHD-32 | Integration Tests - Workflows | 3h | 📋 Not Started |
| ADHD-33 | UI Polish & Bug Fixes | 3h | 📋 Not Started |

**Total: ~11 hours** (3 sessions)

## Total Project Estimate

**~89 hours** across **~25 sessions**

Each session stays well under the 4-hour limit with buffer time.

## How to Use This Plan

### For Each Story:

1. **Read the story card** in the appropriate epic folder
2. **Check prerequisites** - ensure previous stories are complete
3. **Open a new Claude session** dedicated to that story
4. **Share the story README** with Claude
5. **Implement step-by-step** following acceptance criteria
6. **Test thoroughly** using the testing checklist
7. **Mark story complete** and commit code
8. **Move to next story**

### Session Tips:

- **One story per session** (or split large stories across 2 sessions)
- **Test as you go** - don't wait until the end
- **Commit frequently** - after each major milestone
- **Take breaks** - ADHD-friendly approach!
- **Ask Claude to explain** any confusing code

## Code Quality Standards

All code must follow these principles:

### Readability
- Clear variable and function names
- Type hints on all functions
- Docstrings for all classes and complex functions
- Comments explaining WHY, not WHAT

### Debuggability
- Comprehensive logging at INFO and DEBUG levels
- Clear error messages with context
- Validation at boundaries (user input, external APIs)
- Assertions for invariants

### Maintainability
- Single Responsibility Principle
- DRY (Don't Repeat Yourself)
- Consistent patterns across codebase
- Small, focused functions (< 50 lines)

### Testing
- Unit tests for business logic
- Integration tests for workflows
- Test edge cases and error conditions
- Test files mirror source structure

## Dependencies Between Stories

```
ADHD-1 (Setup)
    ↓
ADHD-2 (Database) → ADHD-3 (Models) → ADHD-4 (Base Repo) → ADHD-5 (Task Repo)
                                                                    ↓
ADHD-6 (Config) → ADHD-7 (LLM Service) ────────────────────────────┤
                      ↓                                             ↓
                  ADHD-8 (Task Service) → ADHD-9 (Calendar Service)
                      ↓                           ↓
                  ADHD-10 (Time Est) ─────────────┤
                      ↓                           ↓
                  ADHD-11 (LangGraph State) ──────┤
                      ↓
            ADHD-12 (Supervisor) → ADHD-13 (Planning) → ADHD-14 (Scheduling)
                      ↓                                          ↓
            ADHD-15 (Suggestion) ──────────────────────────────┤
                      ↓                                          ↓
            ADHD-16 (Graph Builder) ───────────────────────────┤
                      ↓
            ADHD-17 (UI Structure) → ADHD-18 (Chat) → ADHD-19 (Tasks)
                      ↓                                      ↓
            ADHD-20 (Calendar View) → ADHD-21 (Settings) ──┤
                      ↓
            ADHD-22 (Apple Perms) → ADHD-23 (Reminders) → ADHD-24 (Calendar)
                      ↓                                          ↓
            ADHD-25 (Sync Service) ────────────────────────────┤
                      ↓
            ADHD-26 (Energy Service) → ADHD-27 (Energy Agent)
                      ↓                          ↓
            ADHD-28 (Sync Agent) → ADHD-29 (Buffer/Context)
                      ↓
            ADHD-30 (Error Handling) → ADHD-31 (Unit Tests)
                      ↓                          ↓
            ADHD-32 (Integration Tests) → ADHD-33 (Polish)
```

## Progress Tracking

Update this section as you complete stories:

- **Completed Stories**: 10/33 ✅
- **Story Cards Created**: ADHD-11 to ADHD-16 (Epic 3)
- **Current Sprint**: Epic 2 - Core Services (ADHD-10 complete, ADHD-11 next)
- **Current Story**: ADHD-10 (Complete) / ADHD-11 (Next)
- **Hours Invested**: ~26 hours
- **Estimated Remaining**: ~63 hours

## Getting Help

If you get stuck on a story:
1. Review the story's implementation notes
2. Check the architecture documentation
3. Look at similar patterns in the codebase
4. Ask Claude to explain a specific concept
5. Take a break and come back fresh!

## Next Steps

1. ✅ ~~Read [ADHD-1: Project Setup](epic-1-foundation/ADHD-1-project-setup.md)~~ - **COMPLETE**
2. ✅ ~~Read [ADHD-2: Database Schema](epic-1-foundation/ADHD-2-database-schema.md)~~ - **COMPLETE**
3. ✅ ~~Read [ADHD-3: Pydantic Models & Enums](epic-1-foundation/ADHD-3-pydantic-models-enums.md)~~ - **COMPLETE**
4. ✅ ~~Read [ADHD-4: Base Repository Pattern](epic-1-foundation/ADHD-4-base-repository-pattern.md)~~ - **COMPLETE**
5. ✅ ~~Read [ADHD-5: Task & TimeBlock Repositories](epic-1-foundation/ADHD-5-task-timeblock-repositories.md)~~ - **COMPLETE**
6. ✅ ~~Read [ADHD-6: Configuration & Logging Enhancement](epic-2-core-services/ADHD-6-configuration-logging-enhancement.md)~~ - **COMPLETE**
7. ✅ ~~Read [ADHD-7: LLM Service & Provider Factory](epic-2-core-services/ADHD-7-llm-service-provider-factory.md)~~ - **COMPLETE**
8. ✅ ~~Read [ADHD-8: Task Service](epic-2-core-services/ADHD-8-task-service.md)~~ - **COMPLETE**
9. ✅ ~~Read [ADHD-9: Calendar Service](epic-2-core-services/ADHD-9-calendar-service.md)~~ - **COMPLETE**
10. ✅ ~~Read [ADHD-10: Time Estimation Service](epic-2-core-services/ADHD-10-time-estimation-service.md)~~ - **COMPLETE**
11. 📍 Read [ADHD-11: LangGraph State & Base Agent](epic-3-agents/ADHD-11-langgraph-state-base-agent.md)

Good luck! Remember: progress over perfection. 🚀
