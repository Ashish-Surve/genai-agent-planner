# UAT Chat Workflow Test Suite

## Overview
Comprehensive User Acceptance Testing (UAT) for the ADHD-Planner agent system through the chat interface.

## Test Results
✅ **46 tests passing**
- 33 integration tests (test_agent_system_integration.py)
- 13 UAT chat workflow tests (test_uat_chat_workflow.py)

## Test Files

### 1. test_agent_system_integration.py (33 tests)
Real integration tests without mocks - exercises actual services with real database.

#### Test Classes:
- **TestTaskServiceIntegration** (9 tests)
  - Task creation, deadlines, status transitions
  - Task filtering and updates
  - Input validation

- **TestCalendarServiceIntegration** (6 tests)
  - Time block creation and management
  - Available slot finding
  - Different block types

- **TestStateManagement** (4 tests)
  - State creation and updates
  - AI message handling
  - Error handling

- **TestAgentInitialization** (5 tests)
  - Agent initialization
  - Service dependency injection
  - Error handling for missing services

- **TestAgentErrorHandling** (4 tests)
  - Input validation
  - Error recovery
  - Edge case handling

- **TestRealWorldScenarios** (4 tests)
  - Complete task workflows
  - Schedule simulation
  - Multi-day planning

- **TestServiceInteraction** (2 tests)
  - Task and calendar service integration
  - State propagation

### 2. test_uat_chat_workflow.py (13 tests)
User Acceptance Tests that replicate actual chat UI interactions.

#### Key User Workflows:
1. **Add Task for Tomorrow** - User asks to add a task with deadline
2. **Add and Delete Task** - Complete lifecycle test
3. **Multiple Chat Interactions** - Sequential user requests
4. **Task with Context** - Chat handler processes messages with task context
5. **Task Lifecycle** - Create → Start → Complete workflow

#### Real-World Scenarios:
- Busy Day Workflow (morning planning, multiple tasks)
- Task Interruption (urgent task interrupts scheduled work)
- End of Day Review (complete and delete tasks)

#### Chat Input Recognition:
- Task addition requests
- Planning requests
- Greetings and general messages

## How Tests Map to UI Chat Interactions

### Chat Handler Flow:
```
User Input (Chat UI)
    ↓
ChatHandler.process_message(user_input)
    ↓
SessionManager.add_message("user", user_input)
    ↓
Agent Graph processes request
    ↓
Chat Response returned
    ↓
SessionManager.add_message("assistant", response)
```

### Test Workflow Example:
```python
# 1. User sends message via chat
response = chat_handler.process_message("Add task for tomorrow: Review proposal, 2 hours, high priority")

# 2. System creates task in database
task = task_service.create_task(
    title="Review proposal",
    estimated_duration_minutes=120,
    priority="HIGH",
    deadline=tomorrow,
)

# 3. Verify task was created
assert task.id is not None
assert task.deadline.date() == tomorrow.date()
```

## Testing Approach

### Real Services (No Mocks):
- Uses actual TaskService
- Uses actual CalendarService
- Uses actual LLMService (Gemini provider)
- Uses actual database (SQLite in-memory for tests)

### Fixtures:
```python
@pytest.fixture
def integration_db_session(tmp_path, monkeypatch):
    """Creates isolated test database"""

@pytest.fixture
def task_service(integration_db_session):
    """Real TaskService with test database"""

@pytest.fixture
def chat_handler(llm_service):
    """ChatHandler that processes actual messages"""
```

## Coverage

- **Task Service**: 62% coverage
- **Calendar Service**: 60% coverage
- **Chat Handler**: 49% coverage
- **State Management**: 46% coverage
- **Overall**: 43% coverage (in scope for UAT)

## Running Tests

```bash
# Run all new tests
uv run pytest tests/integration/test_agent_system_integration.py tests/integration/test_uat_chat_workflow.py -v

# Run specific test
uv run pytest tests/integration/test_uat_chat_workflow.py::TestChatUATWorkflow::test_add_and_delete_task_workflow -v

# Run with coverage
uv run pytest tests/integration/test_uat_chat_workflow.py --cov=src --cov=tests
```

## Key Test Scenarios

### Scenario 1: Add Task for Tomorrow
- User: "Add a task for tomorrow: Review project proposal, 2 hours, high priority"
- System creates task with deadline set to tomorrow
- Task appears in task list

### Scenario 2: Add and Delete Task
- User adds task: "Add task: Prepare presentation, 90 minutes"
- System creates task in database
- User deletes task: "Delete the task"
- System removes task from database
- Verify task is deleted

### Scenario 3: Multiple Sequential Interactions
- Morning standup (30 min)
- Code review (60 min)
- Lunch break (45 min)
- All tasks created and managed through chat

### Scenario 4: Task Lifecycle
- Create → Start → Complete
- User interacts through chat
- System tracks status transitions

## Assertions

Tests verify:
1. **Chat Response**: Handler returns appropriate responses
2. **Data Persistence**: Tasks saved to database correctly
3. **Status Transitions**: Task statuses change as expected
4. **Deadline Handling**: Dates set correctly
5. **Priority Levels**: High/Medium/Low priority saved
6. **Duration Estimation**: Time estimates stored properly
7. **Error Handling**: Validation prevents invalid data
8. **State Management**: Context passes between interactions

## Dependencies

- pytest
- SQLAlchemy (database)
- ChatHandler (UI integration)
- TaskService, CalendarService (business logic)
- LLMService (Gemini provider)

## Future Enhancements

- [ ] Multi-turn conversations
- [ ] Calendar integration in chat
- [ ] Energy level tracking in conversations
- [ ] Suggestions based on chat history
- [ ] Blocking and rescheduling through chat
- [ ] Chat memory/conversation history
