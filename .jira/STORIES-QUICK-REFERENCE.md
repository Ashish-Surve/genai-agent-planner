# All Stories - Quick Reference

## Epic 1: Foundation (Stories 1-5)

### ✅ ADHD-1: Project Setup & Configuration [READY]
**Time**: 2h | **Files**: config.py, logger.py, __init__.py files
- Set up directory structure
- Configuration management with pydantic-settings
- Logging infrastructure
- Test framework setup

### ✅ ADHD-2: Database Schema & Migrations [READY]
**Time**: 3h | **Files**: schema.py, connection.py, setup_database.py
- SQLAlchemy models for all entities
- Alembic for migrations
- Database connection pooling
- Initialization script

### ADHD-3: Pydantic Models & Enums
**Time**: 2h | **Files**: models/*.py, enums.py
- Pydantic models mirroring database schema
- All enums (EnergyLevel, Priority, TaskStatus, etc.)
- Validation rules
- Type conversions

### ADHD-4: Base Repository Pattern
**Time**: 2h | **Files**: repositories/base_repository.py
- Generic base repository with CRUD operations
- Query helpers
- Transaction management
- Error handling

### ADHD-5: Task & TimeBlock Repositories
**Time**: 3h | **Files**: repositories/task_repository.py, time_block_repository.py
- Task-specific queries (by status, deadline, etc.)
- TimeBlock queries (by date range, conflicts)
- Relationship handling
- Filtering and sorting

---

## Epic 2: Core Services (Stories 6-10)

### ADHD-6: Configuration & Logging Enhancement
**Time**: 2h | **Files**: utils/validation.py, utils/time_utils.py
- Input validation helpers
- Time/date utilities
- Enhanced logging with context
- Error formatting

### ADHD-7: LLM Service & Provider Factory
**Time**: 3h | **Files**: integrations/llm/*.py, services/llm_service.py
- Provider factory pattern
- Ollama provider implementation
- Gemini provider implementation
- Claude provider implementation
- Prompt management

### ADHD-8: Task Service
**Time**: 3h | **Files**: services/task_service.py
- Task CRUD with business logic
- Status transitions
- Dependency checking
- Recurrence handling

### ADHD-9: Calendar Service
**Time**: 3h | **Files**: services/calendar_service.py
- TimeBlock management
- Availability checking
- Conflict detection
- Schedule generation helpers

### ADHD-10: Time Estimation Service
**Time**: 2h | **Files**: services/time_estimation_service.py
- Historical analysis
- LLM-based estimation
- Accuracy tracking
- Learning from actuals

---

## Epic 3: LangGraph Agents (Stories 11-16)

### ADHD-11: LangGraph State & Base Agent
**Time**: 3h | **Files**: graph/state.py, agents/base.py
- AgentState TypedDict
- BaseAgent abstract class
- Agent utilities
- State management helpers

### ADHD-12: Supervisor Agent
**Time**: 3h | **Files**: agents/supervisor.py, graph/edges.py
- Request routing logic
- Intent classification
- Multi-agent coordination
- Response synthesis

### ADHD-13: Planning Agent
**Time**: 3h | **Files**: agents/planning_agent.py, utils/prompts/planning_prompts.py
- Natural language task extraction
- Time/energy estimation with LLM
- Calendar availability checking
- Scheduling suggestions

### ADHD-14: Scheduling Agent
**Time**: 4h | **Files**: agents/scheduling_agent.py, utils/prompts/scheduling_prompts.py
- Schedule generation with constraints
- ADHD-friendly rules application
- Energy level matching
- Multiple schedule options

### ADHD-15: Suggestion Agent
**Time**: 2h | **Files**: agents/suggestion_agent.py, utils/prompts/suggestion_prompts.py
- Context analysis
- Task ranking by suitability
- Recommendation generation
- Reasoning explanation

### ADHD-16: Graph Builder & Integration
**Time**: 3h | **Files**: graph/builder.py, graph/nodes.py
- Graph construction
- Node functions
- Edge routing
- Testing with mock LLM

---

## Epic 4: Streamlit UI (Stories 17-21)

### ADHD-17: Streamlit App Structure
**Time**: 2h | **Files**: ui/app.py, core/session_manager.py
- Main app entry point
- Page routing
- Session state management
- Navigation sidebar

### ADHD-18: Chat Page & Components
**Time**: 3h | **Files**: ui/pages/chat.py, ui/components/chat_*.py
- Chat interface
- Message display
- Input handling
- Agent integration

### ADHD-19: Tasks Page & Components
**Time**: 3h | **Files**: ui/pages/tasks.py, ui/components/task_card.py
- Task list with filtering
- Task card component
- Quick actions
- Sync status display

### ADHD-20: Calendar View
**Time**: 4h | **Files**: ui/pages/calendar_view.py, ui/components/time_block*.py
- Week/day views
- TimeBlock rendering
- Drag-and-drop (future)
- Energy visualization

### ADHD-21: Settings Page
**Time**: 2h | **Files**: ui/pages/settings.py
- User preferences form
- LLM configuration
- Energy patterns editor
- Sync settings

---

## Epic 5: Apple Integration (Stories 22-25)

### ADHD-22: Apple Permissions & Setup
**Time**: 2h | **Files**: integrations/apple/permissions.py, scripts/test_apple_permissions.py
- Permission request handling
- EventKit initialization
- Status checking
- Error handling

### ADHD-23: Reminders Integration
**Time**: 3h | **Files**: integrations/apple/reminders.py
- Create/read/update/delete reminders
- Data mapping (Task ↔ EKReminder)
- List management
- Error handling

### ADHD-24: Calendar Integration
**Time**: 3h | **Files**: integrations/apple/calendar.py
- Create/read/update/delete events
- Data mapping (TimeBlock ↔ EKEvent)
- Calendar selection
- Recurrence rules

### ADHD-25: Sync Service & Conflict Resolution
**Time**: 4h | **Files**: services/sync_service.py, repositories/sync_operation_repository.py
- Sync queue management
- Bidirectional sync logic
- Conflict detection
- Resolution strategies
- Background polling

---

## Epic 6: ADHD Features (Stories 26-29)

### ADHD-26: Energy Service & Logging
**Time**: 2h | **Files**: services/energy_service.py, repositories/energy_log_repository.py
- Energy logging
- Pattern storage
- Query helpers
- Data aggregation

### ADHD-27: Energy Agent & Pattern Analysis
**Time**: 3h | **Files**: agents/energy_agent.py
- Pattern analysis
- Energy prediction
- Accuracy tracking
- Learning algorithm

### ADHD-28: Sync Agent
**Time**: 2h | **Files**: agents/sync_agent.py
- Sync operation processing
- Status updates
- Error handling
- Retry logic

### ADHD-29: Buffer Time & Context Switching
**Time**: 2h | **Files**: Update scheduling_agent.py, calendar_service.py
- Buffer time calculation
- Context switch detection
- Penalty application
- Schedule optimization

---

## Epic 7: Polish & Testing (Stories 30-33)

### ADHD-30: Error Handling & Logging
**Time**: 2h | **Files**: core/exceptions.py, update all services
- Custom exceptions
- Error middleware
- User-friendly messages
- Comprehensive logging

### ADHD-31: Unit Tests - Core Services
**Time**: 3h | **Files**: tests/unit/test_services/*.py
- TaskService tests
- CalendarService tests
- LLMService tests with mocks
- Repository tests

### ADHD-32: Integration Tests - Workflows
**Time**: 3h | **Files**: tests/integration/*.py
- Task creation workflow
- Schedule generation workflow
- Sync workflow
- Agent orchestration

### ADHD-33: UI Polish & Bug Fixes
**Time**: 3h | **Files**: Various UI files, bug fixes
- UI refinement
- Error messages
- Loading states
- Performance optimization

---

## Story Dependencies

```
1 → 2 → 3 → 4 → 5
         ↓
    6 → 7 → 8 → 9 → 10
              ↓
         11 → 12 → 13 → 14 → 15 → 16
                        ↓
                   17 → 18 → 19 → 20 → 21
                        ↓
                   22 → 23 → 24 → 25
                        ↓
                   26 → 27 → 28 → 29
                        ↓
                   30 → 31 → 32 → 33
```

## How to Use This Guide

1. **Start with ADHD-1** - Full detailed card available
2. **Read the detailed card** in `.jira/epic-X/` folder
3. **If card doesn't exist**, use this quick reference to understand scope
4. **Ask Claude to create the detailed card** when you're ready to implement
5. **Implement following the pattern** from detailed cards
6. **Mark complete and move to next**

## Creating Missing Story Cards

When you're ready to implement a story that doesn't have a detailed card yet:

```
Hey Claude, I'm ready to work on ADHD-X: [Story Title].

Can you create a detailed story card following the same format as
ADHD-1 and ADHD-2? Include:
- Implementation steps
- Code examples
- Testing checklist
- Success criteria

Use the quick reference in STORIES-QUICK-REFERENCE.md for the scope.
```

## Estimated Timeline

- **Epic 1**: 12h (3 sessions of 4h)
- **Epic 2**: 13h (4 sessions)
- **Epic 3**: 18h (5 sessions)
- **Epic 4**: 14h (4 sessions)
- **Epic 5**: 12h (3 sessions)
- **Epic 6**: 9h (3 sessions)
- **Epic 7**: 11h (3 sessions)

**Total**: ~89 hours across ~25 sessions

## Tips for Success

1. **One story at a time** - Don't skip ahead
2. **Test thoroughly** - Each story has acceptance criteria
3. **Commit after each story** - Clean git history
4. **Take breaks** - 4 hours is a long session!
5. **Ask questions** - Claude can explain any concept
6. **Follow patterns** - Consistency is key
7. **Read the architecture docs** - Context helps

## Progress Tracking

Update `.jira/README.md` with your progress after each story!
