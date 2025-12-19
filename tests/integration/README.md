# Integration Tests for ADHD-Planner Streamlit UI

This directory contains comprehensive integration tests for the ADHD-Planner application, covering all Streamlit UI pages and backend services.

## Overview

- **Total Tests**: 234
- **Test Files**: 5
- **Test Categories**: Tasks, Chat, Calendar, Settings, End-to-End Workflows

## Test Files

### 1. `test_streamlit_tasks_page.py` (45 tests)
Tests for the Tasks page and TaskService.

**Coverage**:
- Task creation with validation
- Task retrieval and filtering
- Task updates and status changes
- Task deletion and dependencies
- Edge cases and error handling

**Key Test Classes**:
- `TestTasksPageCreation` - Creating tasks
- `TestTasksPageRetrieval` - Getting tasks
- `TestTasksPageUpdate` - Updating tasks
- `TestTasksPageDelete` - Deleting tasks
- `TestTasksPageFiltering` - Filtering and sorting
- `TestTasksPageIntegration` - Complete workflows

### 2. `test_streamlit_chat_page.py` (47 tests)
Tests for the Chat page, ChatHandler, and SessionManager.

**Coverage**:
- Message processing and intent recognition
- Task creation through chat
- Scheduling and planning
- Session management and context
- Error handling and recovery

**Key Test Classes**:
- `TestChatHandlerBasic` - Basic chat operations
- `TestChatSessionManagement` - Session state
- `TestChatHandlerIntentRecognition` - Intent detection
- `TestChatHandlerMultiTurn` - Multi-turn conversations
- `TestChatHandlerIntegration` - Complete workflows

### 3. `test_streamlit_calendar_page.py` (63 tests)
Tests for the Calendar page and CalendarService.

**Coverage**:
- Time block creation and management
- Conflict detection and resolution
- Availability checking and slot finding
- Schedule navigation and summaries
- Energy level considerations

**Key Test Classes**:
- `TestCalendarTimeBlockCreation` - Creating blocks
- `TestCalendarConflictDetection` - Detecting conflicts
- `TestCalendarAvailability` - Finding free time
- `TestCalendarUpdate` - Updating blocks
- `TestCalendarIntegration` - Complete workflows

### 4. `test_streamlit_settings_page.py` (47 tests)
Tests for the Settings page and SettingsManager.

**Coverage**:
- LLM provider configuration
- Working hours settings
- Energy level preferences
- Apple sync configuration
- Settings persistence and import/export

**Key Test Classes**:
- `TestSettingsLLMConfiguration` - LLM setup
- `TestSettingsWorkingHours` - Schedule config
- `TestSettingsEnergyLevels` - Energy preferences
- `TestSettingsPersistence` - File persistence
- `TestSettingsImportExport` - Data import/export

### 5. `test_e2e_workflows.py` (32 tests)
End-to-end tests for complete user workflows.

**Coverage**:
- User onboarding and setup
- Daily productivity workflows
- Weekly planning
- Task dependencies and blocking
- Priority management and overdue handling
- Context switching and error recovery

**Key Test Classes**:
- `TestUserOnboarding` - Initial setup
- `TestDailyProductivityWorkflow` - Daily routines
- `TestWeeklyPlanning` - Weekly planning
- `TestTaskDependencies` - Task chains
- `TestProductivityMetrics` - Tracking stats

## Running Tests

### Setup

```bash
# Navigate to project root
cd /Users/devwork/Developer/ADHD-Planner

# Activate virtual environment
source .venv/bin/activate

# Ensure all dependencies installed
pip install -e .
```

### Run All Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with coverage report
pytest tests/integration/ -v --cov=src --cov-report=html

# Run with detailed output
pytest tests/integration/ -vv --tb=long
```

### Run Specific Test File

```bash
# Run Tasks page tests only
pytest tests/integration/test_streamlit_tasks_page.py -v

# Run Chat page tests only
pytest tests/integration/test_streamlit_chat_page.py -v

# Run Calendar page tests only
pytest tests/integration/test_streamlit_calendar_page.py -v

# Run Settings page tests only
pytest tests/integration/test_streamlit_settings_page.py -v

# Run E2E tests only
pytest tests/integration/test_e2e_workflows.py -v
```

### Run Specific Test Class

```bash
# Test task creation
pytest tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation -v

# Test chat handler
pytest tests/integration/test_streamlit_chat_page.py::TestChatHandlerBasic -v

# Test calendar blocks
pytest tests/integration/test_streamlit_calendar_page.py::TestCalendarTimeBlockCreation -v
```

### Run Specific Test

```bash
# Run single test
pytest tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation::test_create_task_with_valid_data -v

# Run with extra output
pytest tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation::test_create_task_with_valid_data -vv -s
```

### Run Tests Matching Pattern

```bash
# Run all task-related tests
pytest tests/integration/ -k "task" -v

# Run all tests that are currently failing
pytest tests/integration/ --tb=short 2>&1 | grep FAILED

# Run tests excluding slow ones
pytest tests/integration/ -m "not slow" -v
```

## Understanding Test Results

### Test Output Format

```
tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation::test_create_task_with_valid_data PASSED [50%]
                                                                                                             ^^^^^^
                                                                           Status: PASSED, FAILED, ERROR, SKIPPED

tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation::test_create_task_with_invalid_duration FAILED [51%]
```

### Status Meanings

- **PASSED** ✅ - Test passed successfully
- **FAILED** ❌ - Test ran but assertion failed
- **ERROR** 🔴 - Test crashed due to exception
- **SKIPPED** ⊘ - Test was skipped (pytest.skip())

### Reading Error Output

```
FAILED tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation::test_create_task_with_invalid_duration

with pytest.raises(ValueError):
    task_service.create_task(
        title="Invalid Task",
        estimated_duration_minutes=-1,
    )
E   Failed: DID NOT RAISE ValueError  # Error: ValueError was not raised as expected
```

## Debugging Tests

### Run with More Output

```bash
# Show print statements
pytest tests/integration/test_streamlit_tasks_page.py -v -s

# Show local variables on failure
pytest tests/integration/test_streamlit_tasks_page.py -v -l

# Stop on first failure
pytest tests/integration/test_streamlit_tasks_page.py -v -x

# Run last failed tests
pytest tests/integration/ --lf -v
```

### Run with Debugging

```bash
# Set breakpoint in code
import pdb; pdb.set_trace()

# Run with breakpoints enabled
pytest tests/integration/test_streamlit_tasks_page.py -v --pdb

# Run and drop to debugger on failure
pytest tests/integration/test_streamlit_tasks_page.py -v --pdb-trace
```

## Test Configuration

### Fixtures

Tests use pytest fixtures defined in `conftest.py`:

- **`test_db_session`** - SQLAlchemy session for test database
- **`sample_task_data`** - Sample task dictionary
- **`temp_settings_file`** - Temporary settings file

### Database

Tests use an in-memory SQLite database for isolation:

```python
@pytest.fixture
def test_db_session():
    """Create test database session."""
    # Database is reset for each test
```

## Common Test Patterns

### Testing Task Creation

```python
def test_create_task(task_service):
    task = task_service.create_task(
        title="Test Task",
        estimated_duration_minutes=30,
        priority=Priority.HIGH,
    )
    assert task is not None
    assert task.title == "Test Task"
```

### Testing Task Updates

```python
def test_update_task(task_service):
    task = task_service.create_task(title="Original", ...)
    updated = task_service.update_task(task.id, title="Updated")
    assert updated.title == "Updated"
```

### Testing Task Retrieval

```python
def test_get_task(task_service):
    created = task_service.create_task(title="Test", ...)
    retrieved = task_service.get_task(created.id)
    assert retrieved.id == created.id
```

### Testing Filtering

```python
def test_filter_tasks(task_service):
    task_service.create_task(title="Task 1", priority=Priority.HIGH, ...)
    task_service.create_task(title="Task 2", priority=Priority.LOW, ...)

    high_priority = task_service.list_tasks(priority=Priority.HIGH)
    assert len(high_priority) == 1
```

### Testing Chat

```python
def test_chat(chat_handler):
    response = chat_handler.process_message("Create a task")
    assert response is not None
    assert "task" in response.lower()
```

## Test Coverage

Generate HTML coverage report:

```bash
pytest tests/integration/ --cov=src --cov-report=html
open htmlcov/index.html
```

View coverage in terminal:

```bash
pytest tests/integration/ --cov=src --cov-report=term-missing
```

## Known Issues

### Settings Manager Tests Failing

Most Settings page tests fail because `SettingsManager` lacks methods:
- `get()` - Not implemented
- `set()` - Not implemented
- `update_multiple()` - Not implemented

**Fix**: Implement these methods in `src/adhd_planner/core/settings_manager.py`

### Calendar Tests Failing

Calendar tests fail because several methods are missing:
- `find_conflicts()` - Conflict detection not implemented
- `is_available()` - Slot checking not implemented
- `find_available_slots()` - Slot finding not implemented

**Fix**: Implement these methods in `src/services/calendar_service.py`

### Task Filtering Not Working

Task filtering tests fail because filter parameters aren't implemented:
- `category` - Not supported
- `requires_focus` - Not supported
- `sort_by` - Not supported

**Fix**: Add parameter support to `TaskService.list_tasks()`

## Contributing

When adding new functionality:

1. **Write tests first** (TDD)
2. **Implement feature** to pass tests
3. **Ensure existing tests pass**
4. **Run coverage** to check coverage
5. **Commit** with passing tests

### Adding New Tests

1. Create test method in appropriate class:
   ```python
   def test_new_feature(self, service):
       result = service.new_method()
       assert result is not None
   ```

2. Follow naming convention:
   - File: `test_<module>.py`
   - Class: `Test<FeatureName>`
   - Method: `test_<specific_behavior>`

3. Use appropriate assertions:
   ```python
   assert x == y              # Equality
   assert x is not None       # Non-null
   assert x in collection     # Membership
   assert isinstance(x, type) # Type check
   with pytest.raises(Error): # Exception check
   ```

4. Add docstrings:
   ```python
   def test_create_task(self):
       """Test creating a task with valid data."""
   ```

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Test Coverage**: https://coverage.readthedocs.io/
- **SQLAlchemy Testing**: https://docs.sqlalchemy.org/en/14/orm/testing.html
- **Test-Driven Development**: https://en.wikipedia.org/wiki/Test-driven_development

## Summary Files

- **TEST_SUITE_SUMMARY.md** - Overview of all tests and pass rates
- **TEST_EXECUTION_REPORT.md** - Detailed execution results and issues found
- **This file** - How to run and understand the tests

## Contact

For questions about tests, see the Jira ticket or project documentation.
