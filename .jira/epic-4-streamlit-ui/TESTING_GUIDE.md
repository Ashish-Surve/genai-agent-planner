# Comprehensive Testing Guide - ADHD-Planner Streamlit UI

## What Was Done

A complete test suite has been created to validate the Streamlit UI and backend services. This includes:

### Test Files Created (5 files, 234 tests)

1. **test_streamlit_tasks_page.py** (45 tests)
   - Tests for Tasks page and TaskService
   - Coverage: Create, read, update, delete, filter, sort, dependencies

2. **test_streamlit_chat_page.py** (47 tests)
   - Tests for Chat page, ChatHandler, and SessionManager
   - Coverage: Message processing, intent recognition, session management

3. **test_streamlit_calendar_page.py** (63 tests)
   - Tests for Calendar page and CalendarService
   - Coverage: Time blocks, conflict detection, availability, scheduling

4. **test_streamlit_settings_page.py** (47 tests)
   - Tests for Settings page and SettingsManager
   - Coverage: LLM config, working hours, energy levels, persistence

5. **test_e2e_workflows.py** (32 tests)
   - End-to-end tests for complete user workflows
   - Coverage: Onboarding, daily routines, weekly planning, dependencies

## Current Test Results

### Summary
- **Total Tests**: 234
- **Passed**: 98 (42%)
- **Failed**: 136 (58%)
- **Errors**: 50

### By Page
| Page | Tests | Passed | Failed | Pass Rate |
|------|-------|--------|--------|-----------|
| Tasks | 45 | 30 | 15 | 67% |
| Chat | 47 | 32 | 15 | 68% |
| Calendar | 63 | 26 | 37 | 41% |
| Settings | 47 | 4 | 43 | 9% |
| E2E | 32 | 6 | 26 | 19% |

## Why Backend is Not Working

The tests reveal specific reasons why the UI is non-functional:

### 1. Settings Manager is Broken (47 test errors)
- **Problem**: Missing `get()` and `set()` methods
- **Impact**: Can't change any settings
- **Files to Fix**: `src/adhd_planner/core/settings_manager.py`
- **Required Methods**:
  ```python
  def get(self, key: str) -> Any
  def set(self, key: str, value: Any) -> None
  def update_multiple(self, updates: dict) -> None
  def export_settings(self) -> dict
  def import_settings(self, data: dict) -> None
  def reset_to_default(self, key: str) -> None
  def save(self) -> None
  def reload(self) -> None
  ```

### 2. Session Manager is Incomplete (8 test failures)
- **Problem**: Missing context and message history methods
- **Impact**: Chat can't maintain multi-turn conversations
- **Files to Fix**: `src/adhd_planner/core/session_manager.py`
- **Required Methods**:
  ```python
  def add_message(self, role: str, content: str) -> None
  def get_message_history(self) -> list
  def clear_history(self) -> None
  def set_context(self, key: str, value: Any) -> None
  def get_context(self, key: str) -> Any
  ```

### 3. Task Service Validation Missing (3 test failures)
- **Problem**: No validation on input data
- **Impact**: Bad data gets into database
- **Files to Fix**: `src/services/task_service.py` (line 90+)
- **Issues**:
  - Empty titles accepted
  - Negative durations accepted
  - Past deadlines accepted

### 4. Task Filtering Not Implemented (4 test failures)
- **Problem**: Filter parameters not supported
- **Impact**: Can't filter tasks by category, priority, focus
- **Files to Fix**: `src/services/task_service.py` (list_tasks method)
- **Missing Filters**:
  - `category` - Filter by context category
  - `requires_focus` - Filter by focus requirements
  - `sort_by` - Sort by deadline, priority, etc.

### 5. Calendar Scheduling Missing (10+ test failures)
- **Problem**: Slot finding and conflict detection not implemented
- **Impact**: Can't schedule tasks, can't detect conflicts
- **Files to Fix**: `src/services/calendar_service.py`
- **Missing Methods**:
  ```python
  def find_conflicts(self, start_time, end_time) -> list
  def is_available(self, start_time, end_time) -> bool
  def find_available_slots(self, date, duration, ...) -> list
  def find_next_available_slot(self, date, duration, ...) -> TimeBlock
  def get_schedule_summary(self, date) -> dict
  ```

### 6. Task Dependencies Incomplete (5 test failures)
- **Problem**: Dependency system not fully implemented
- **Impact**: Can't create task chains or block on dependencies
- **Files to Fix**: `src/services/task_service.py` + `src/repositories/`
- **Issues**:
  - `depends_on` parameter not handled
  - `get_tasks_ready_to_start()` broken
  - Dependency checking on delete missing

## How to Run Tests

### Quick Start

```bash
cd /Users/devwork/Developer/ADHD-Planner
source .venv/bin/activate

# Run all tests
pytest tests/integration/ -v

# Run specific page tests
pytest tests/integration/test_streamlit_tasks_page.py -v
pytest tests/integration/test_streamlit_chat_page.py -v
pytest tests/integration/test_streamlit_calendar_page.py -v
pytest tests/integration/test_streamlit_settings_page.py -v
pytest tests/integration/test_e2e_workflows.py -v
```

### With Coverage Report

```bash
pytest tests/integration/ -v --cov=src --cov-report=html
open htmlcov/index.html
```

### Run Specific Test

```bash
# Run one test
pytest tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation::test_create_task_with_valid_data -v

# Run test class
pytest tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation -v

# Find tests with keyword
pytest tests/integration/ -k "filter" -v
```

## Test Location Reference

All test files are in: `/Users/devwork/Developer/ADHD-Planner/tests/integration/`

| File | Tests | Purpose |
|------|-------|---------|
| test_streamlit_tasks_page.py | 45 | Tasks page & service tests |
| test_streamlit_chat_page.py | 47 | Chat page & handlers tests |
| test_streamlit_calendar_page.py | 63 | Calendar page & service tests |
| test_streamlit_settings_page.py | 47 | Settings page & manager tests |
| test_e2e_workflows.py | 32 | End-to-end workflows |
| README.md | - | How to run and understand tests |

Documentation files:
- `.jira/epic-4-streamlit-ui/TEST_SUITE_SUMMARY.md` - Overview
- `.jira/epic-4-streamlit-ui/TEST_EXECUTION_REPORT.md` - Detailed results
- `.jira/epic-4-streamlit-ui/TESTING_GUIDE.md` - This file

## What Tests Cover

### Tasks Page Tests (45 tests)
- ✅ Creating tasks with validation
- ✅ Retrieving tasks by ID
- ✅ Updating task properties
- ✅ Completing and starting tasks
- ✅ Deleting tasks
- ⚠️ Filtering by category, priority, focus
- ⚠️ Sorting tasks
- ⚠️ Task dependencies
- ⚠️ Overdue detection

### Chat Page Tests (47 tests)
- ✅ Message processing
- ✅ Intent recognition
- ✅ Task creation via chat
- ✅ Scheduling via chat
- ✅ Planning via chat
- ⚠️ Session message history
- ⚠️ Multi-turn conversations
- ⚠️ Context preservation
- ⚠️ Error recovery

### Calendar Page Tests (63 tests)
- ✅ Creating time blocks
- ✅ Retrieving blocks for dates
- ✅ Deleting blocks
- ✅ Date navigation
- ⚠️ Conflict detection
- ⚠️ Availability checking
- ⚠️ Slot finding
- ⚠️ Schedule summaries
- ⚠️ Energy level filtering

### Settings Page Tests (47 tests)
- ❌ LLM provider configuration
- ❌ API key settings
- ❌ Working hours configuration
- ❌ Energy level settings
- ❌ Apple sync settings
- ❌ Display settings
- ⚠️ Settings persistence
- ❌ Import/export

### E2E Workflow Tests (32 tests)
- ✅ Daily productivity workflows
- ✅ Weekly planning
- ✅ Priority management
- ⚠️ User onboarding
- ⚠️ Task dependencies
- ⚠️ Overdue management
- ✅ Error recovery

Legend: ✅ Working | ⚠️ Partial | ❌ Broken

## How to Fix Issues

### Priority 1 - Fix These First (Do Today)

#### Fix #1: Implement SettingsManager Methods (2 hours)
```python
# File: src/adhd_planner/core/settings_manager.py

def get(self, key: str, default=None):
    """Get a setting value."""
    return self.settings.get(key, default)

def set(self, key: str, value):
    """Set a setting value."""
    self.settings[key] = value

def save(self):
    """Save settings to file."""
    with open(self.config_file, 'w') as f:
        json.dump(self.settings, f)
```

Run test after fix:
```bash
pytest tests/integration/test_streamlit_settings_page.py::TestSettingsLLMConfiguration -v
```

#### Fix #2: Add TaskService Input Validation (1 hour)
```python
# File: src/services/task_service.py in create_task()

if not title or not title.strip():
    raise ValueError("Task title cannot be empty")

if estimated_duration_minutes <= 0:
    raise ValueError("Duration must be positive")

if deadline and deadline < datetime.now():
    raise ValueError("Deadline cannot be in the past")
```

Run test after fix:
```bash
pytest tests/integration/test_streamlit_tasks_page.py::TestTasksPageCreation -v
```

#### Fix #3: Implement SessionManager Context Methods (1 hour)
```python
# File: src/adhd_planner/core/session_manager.py

def add_message(self, role: str, content: str):
    """Add message to history."""
    if "messages" not in self.state:
        self.state["messages"] = []
    self.state["messages"].append({"role": role, "content": content})

def get_message_history(self):
    """Get all messages."""
    return self.state.get("messages", [])

def set_context(self, key: str, value):
    """Set context value."""
    self.state[key] = value
```

Run test after fix:
```bash
pytest tests/integration/test_streamlit_chat_page.py::TestChatSessionManagement -v
```

### Priority 2 - Fix in Next Iteration

#### Fix #4: Implement Task Filtering
- Add `category` parameter to `list_tasks()`
- Add `requires_focus` filtering
- Add `sort_by` parameter
- Test: `pytest tests/integration/test_streamlit_tasks_page.py::TestTasksPageFiltering -v`

#### Fix #5: Implement Calendar Scheduling
- Add `find_conflicts()` method
- Add `is_available()` method
- Add `find_available_slots()` method
- Test: `pytest tests/integration/test_streamlit_calendar_page.py::TestCalendarAvailability -v`

#### Fix #6: Complete Task Dependencies
- Support `depends_on` parameter
- Implement `get_tasks_ready_to_start()`
- Add dependency checking on delete
- Test: `pytest tests/integration/test_streamlit_tasks_page.py::TestTasksPageTaskDependencies -v`

## Using Test Results to Debug

### Example: Settings Not Saving
When test fails:
```
FAILED test_streamlit_settings_page.py::TestSettingsPersistence::test_settings_persist_to_file
AttributeError: 'SettingsManager' object has no attribute 'set'
```

This means: `SettingsManager.set()` method not implemented.

**Fix**: Add the method to `src/adhd_planner/core/settings_manager.py`

### Example: Task Filtering Broken
When test fails:
```
FAILED test_streamlit_tasks_page.py::TestTasksPageFiltering::test_filter_by_category
AssertionError: assert 0 == 1
```

This means: No tasks returned for category filter.

**Fix**: Add `category` parameter handling to `TaskService.list_tasks()`

## Success Criteria

After fixes, target these test pass rates:

- **Tasks Page**: 100% (currently 67%)
- **Chat Page**: 90% (currently 68%)
- **Calendar Page**: 80% (currently 41%)
- **Settings Page**: 100% (currently 9%)
- **E2E Workflows**: 90% (currently 19%)
- **Overall**: 90%+ (currently 42%)

## Next Steps

1. **Read the test failures** - Each failure indicates a missing feature
2. **Run the tests** - See exactly what's broken
3. **Fix issues in priority order** - Start with SettingsManager
4. **Re-run tests** - Verify fixes work
5. **Repeat** - Fix next priority issue

## Test Development Tips

### Understanding a Test

```python
def test_create_task_with_valid_data(self, task_service, sample_task_data):
    # Arrange: Set up test data
    # Act: Call the method
    task = task_service.create_task(**sample_task_data)

    # Assert: Check the result
    assert task is not None
    assert task.title == sample_task_data["title"]
    assert task.status == TaskStatus.NOT_STARTED
```

### When a Test Fails

1. Read the error message carefully
2. Check what assertion failed
3. Look at the test code to understand what it's testing
4. Find the method being tested
5. Add validation or implement missing method

### Debugging with Print Statements

```bash
# Add print to test and run with -s flag
pytest tests/integration/test_file.py::TestClass::test_method -v -s

# Prints show in output
```

## Summary

- **234 tests created** covering all pages and workflows
- **98 tests currently passing** (core functionality works)
- **136 tests failing** due to missing features and validation
- **Key issue**: SettingsManager missing 8+ methods
- **Expected fix time**: 2-4 hours for high-priority items
- **Target**: 90%+ test pass rate within 1 sprint

The tests provide a clear roadmap. Focus on the failures to understand exactly what needs to be implemented.

---

**For detailed information, see:**
- TEST_SUITE_SUMMARY.md - Overview of all tests
- TEST_EXECUTION_REPORT.md - Detailed failure analysis
- tests/integration/README.md - How to run tests
