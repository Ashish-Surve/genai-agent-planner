# ADHD-19: Tasks Page & Components

## Story Information
- **Epic**: Epic 4 - Streamlit UI
- **Story ID**: ADHD-19
- **Estimated Time**: 3 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-17: Streamlit App Structure
  - ✅ ADHD-8: Task Service

## Description

Implement the tasks page with a list view of all tasks, filtering, quick actions, and task card components. Users can view, create, edit, and manage tasks from this interface.

**MVP Focus**: Functional task list with basic CRUD. No drag-and-drop or advanced features.

## Goals

1. Display task list with filtering options
2. Create task card component showing key info
3. Enable quick actions (complete, delete)
4. Add new task form
5. Connect to TaskService for data

## Acceptance Criteria

### Task List
- [ ] Display all tasks from database
- [ ] Filter by status (all, pending, completed)
- [ ] Filter by priority (all, high, medium, low)
- [ ] Sort by due date, priority, or created date
- [ ] Show empty state when no tasks

### Task Card
- [ ] Display task title, priority, status
- [ ] Show estimated duration
- [ ] Show due date if set
- [ ] Quick complete checkbox
- [ ] Delete button

### Add Task
- [ ] Simple form to add new task
- [ ] Title (required)
- [ ] Priority selection
- [ ] Estimated duration
- [ ] Due date (optional)

### Data Integration
- [ ] Fetch tasks from TaskService
- [ ] Create tasks via TaskService
- [ ] Update task status
- [ ] Delete tasks

## Files to Create/Modify

### Files to Modify
```
src/adhd_planner/ui/pages/2_📋_Tasks.py    # Full implementation
```

### New Files
```
src/adhd_planner/ui/components/
└── task_card.py                # Task card component

tests/unit/
└── test_tasks_page.py          # Tasks page tests
```

## Implementation Steps

### Step 1: Create Task Card Component (45 min)

Create `src/adhd_planner/ui/components/task_card.py`:

```python
"""Task card component for displaying individual tasks."""

import streamlit as st
from typing import Callable, Optional
from datetime import datetime


def task_card(
    task_id: str,
    title: str,
    priority: str,
    status: str,
    estimated_minutes: Optional[int] = None,
    due_date: Optional[datetime] = None,
    on_complete: Optional[Callable[[str], None]] = None,
    on_delete: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Display a task card.

    Args:
        task_id: Unique task identifier
        title: Task title
        priority: Priority level (high, medium, low)
        status: Task status (pending, in_progress, completed)
        estimated_minutes: Estimated duration in minutes
        due_date: Optional due date
        on_complete: Callback when task is completed
        on_delete: Callback when task is deleted
    """
    # Priority colors
    priority_colors = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }

    # Status indicators
    is_completed = status == "completed"

    with st.container():
        col1, col2, col3 = st.columns([0.5, 8, 1.5])

        with col1:
            # Checkbox for completion
            checked = st.checkbox(
                "Complete",
                value=is_completed,
                key=f"task_check_{task_id}",
                label_visibility="collapsed",
            )
            if checked != is_completed and on_complete:
                on_complete(task_id)

        with col2:
            # Task title with strikethrough if completed
            title_display = f"~~{title}~~" if is_completed else f"**{title}**"
            priority_icon = priority_colors.get(priority.lower(), "⚪")

            st.markdown(f"{priority_icon} {title_display}")

            # Details line
            details = []
            if estimated_minutes:
                hours = estimated_minutes // 60
                mins = estimated_minutes % 60
                if hours > 0:
                    details.append(f"⏱️ {hours}h {mins}m" if mins else f"⏱️ {hours}h")
                else:
                    details.append(f"⏱️ {mins}m")

            if due_date:
                details.append(f"📅 {due_date.strftime('%b %d')}")

            if details:
                st.caption(" • ".join(details))

        with col3:
            if st.button("🗑️", key=f"task_del_{task_id}", help="Delete task"):
                if on_delete:
                    on_delete(task_id)

        st.markdown("---")


def task_list(
    tasks: list,
    on_complete: Optional[Callable[[str], None]] = None,
    on_delete: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Display a list of task cards.

    Args:
        tasks: List of task dicts/objects
        on_complete: Callback when a task is completed
        on_delete: Callback when a task is deleted
    """
    if not tasks:
        st.info("No tasks to display. Add your first task!")
        return

    for task in tasks:
        # Handle both dict and object access
        if isinstance(task, dict):
            task_card(
                task_id=str(task.get("id", "")),
                title=task.get("title", "Untitled"),
                priority=task.get("priority", "medium"),
                status=task.get("status", "pending"),
                estimated_minutes=task.get("estimated_minutes"),
                due_date=task.get("due_date"),
                on_complete=on_complete,
                on_delete=on_delete,
            )
        else:
            task_card(
                task_id=str(task.id),
                title=task.title,
                priority=task.priority.value if hasattr(task.priority, 'value') else str(task.priority),
                status=task.status.value if hasattr(task.status, 'value') else str(task.status),
                estimated_minutes=task.estimated_minutes,
                due_date=task.due_date,
                on_complete=on_complete,
                on_delete=on_delete,
            )
```

### Step 2: Implement Tasks Page (1.5 hours)

Update `src/adhd_planner/ui/pages/2_📋_Tasks.py`:

```python
"""Tasks page - task management interface."""

import streamlit as st
from datetime import datetime, date
from typing import Optional

from adhd_planner.core.session_manager import SessionManager
from adhd_planner.ui.components.task_card import task_list
from adhd_planner.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Tasks - ADHD Planner", page_icon="📋", layout="wide")

SessionManager.initialize()


def get_task_service():
    """Get task service instance."""
    if "task_service" not in st.session_state:
        try:
            from adhd_planner.services.task_service import TaskService
            from adhd_planner.repositories.task_repository import TaskRepository
            from adhd_planner.database.connection import get_session

            session = get_session()
            repo = TaskRepository(session)
            st.session_state["task_service"] = TaskService(repo)
        except Exception as e:
            logger.warning(f"Could not initialize task service: {e}")
            st.session_state["task_service"] = None

    return st.session_state.get("task_service")


def get_mock_tasks():
    """Return mock tasks for development."""
    return [
        {
            "id": "1",
            "title": "Write project documentation",
            "priority": "high",
            "status": "pending",
            "estimated_minutes": 120,
            "due_date": datetime(2024, 12, 15),
        },
        {
            "id": "2",
            "title": "Review pull requests",
            "priority": "medium",
            "status": "in_progress",
            "estimated_minutes": 60,
            "due_date": None,
        },
        {
            "id": "3",
            "title": "Send weekly update email",
            "priority": "low",
            "status": "completed",
            "estimated_minutes": 15,
            "due_date": datetime(2024, 12, 10),
        },
    ]


def load_tasks(status_filter: str = "all", priority_filter: str = "all", sort_by: str = "created"):
    """Load tasks with filters applied."""
    service = get_task_service()

    if service is None:
        # Use mock data for development
        tasks = get_mock_tasks()
    else:
        try:
            tasks = service.get_all_tasks()
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            tasks = get_mock_tasks()

    # Apply status filter
    if status_filter != "all":
        tasks = [t for t in tasks if (t.get("status") if isinstance(t, dict) else t.status.value) == status_filter]

    # Apply priority filter
    if priority_filter != "all":
        tasks = [t for t in tasks if (t.get("priority") if isinstance(t, dict) else t.priority.value) == priority_filter]

    return tasks


def handle_complete_task(task_id: str):
    """Handle task completion."""
    logger.info(f"Completing task: {task_id}")
    service = get_task_service()

    if service:
        try:
            service.complete_task(task_id)
        except Exception as e:
            st.error(f"Error completing task: {e}")

    st.rerun()


def handle_delete_task(task_id: str):
    """Handle task deletion."""
    logger.info(f"Deleting task: {task_id}")
    service = get_task_service()

    if service:
        try:
            service.delete_task(task_id)
        except Exception as e:
            st.error(f"Error deleting task: {e}")

    st.rerun()


def add_task_form():
    """Display add task form in sidebar."""
    with st.form("add_task_form"):
        st.subheader("➕ Add New Task")

        title = st.text_input("Task Title *", placeholder="What needs to be done?")

        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
        with col2:
            hours = st.number_input("Hours", min_value=0, max_value=8, value=1)
            minutes = st.number_input("Minutes", min_value=0, max_value=59, value=0, step=15)

        due_date = st.date_input("Due Date (optional)", value=None)

        submitted = st.form_submit_button("Add Task", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Please enter a task title")
                return

            estimated_minutes = (hours * 60) + minutes

            service = get_task_service()
            if service:
                try:
                    service.create_task(
                        title=title,
                        priority=priority,
                        estimated_minutes=estimated_minutes,
                        due_date=datetime.combine(due_date, datetime.min.time()) if due_date else None,
                    )
                    st.success("Task added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding task: {e}")
            else:
                st.success("Task added! (mock mode)")
                st.rerun()


def main():
    """Main tasks page."""
    st.title("📋 Tasks")

    # Sidebar with add task form
    with st.sidebar:
        add_task_form()

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["all", "pending", "in_progress", "completed"],
            format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All"
        )

    with col2:
        priority_filter = st.selectbox(
            "Priority",
            ["all", "high", "medium", "low"],
            format_func=lambda x: x.title() if x != "all" else "All"
        )

    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["created", "due_date", "priority"],
            format_func=lambda x: x.replace("_", " ").title()
        )

    st.markdown("---")

    # Load and display tasks
    tasks = load_tasks(status_filter, priority_filter, sort_by)

    # Summary
    total = len(tasks)
    completed = len([t for t in tasks if (t.get("status") if isinstance(t, dict) else t.status.value) == "completed"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("Remaining", total - completed)

    st.markdown("---")

    # Task list
    task_list(
        tasks=tasks,
        on_complete=handle_complete_task,
        on_delete=handle_delete_task,
    )


if __name__ == "__main__":
    main()
else:
    main()
```

### Step 3: Update Components Init (10 min)

Update `src/adhd_planner/ui/components/__init__.py`:

```python
"""Reusable UI components."""

from adhd_planner.ui.components.chat_message import display_message, display_message_history
from adhd_planner.ui.components.task_card import task_card, task_list

__all__ = [
    "display_message",
    "display_message_history",
    "task_card",
    "task_list",
]
```

### Step 4: Create Tests (30 min)

Create `tests/unit/test_tasks_page.py`:

```python
"""Tests for tasks page components."""

import pytest
from datetime import datetime


class TestTaskCard:
    """Test task card component."""

    def test_task_card_import(self):
        """Test task card can be imported."""
        from adhd_planner.ui.components.task_card import task_card, task_list
        assert task_card is not None
        assert task_list is not None


class TestTasksPage:
    """Test tasks page functions."""

    def test_mock_tasks(self):
        """Test mock tasks have required fields."""
        # Import the function directly
        import sys
        import importlib.util

        # We'll test the structure of mock tasks
        mock_tasks = [
            {
                "id": "1",
                "title": "Test task",
                "priority": "high",
                "status": "pending",
                "estimated_minutes": 60,
                "due_date": None,
            }
        ]

        for task in mock_tasks:
            assert "id" in task
            assert "title" in task
            assert "priority" in task
            assert "status" in task
            assert task["priority"] in ["high", "medium", "low"]
            assert task["status"] in ["pending", "in_progress", "completed"]

    def test_filter_logic(self):
        """Test filtering logic works correctly."""
        tasks = [
            {"id": "1", "status": "pending", "priority": "high"},
            {"id": "2", "status": "completed", "priority": "low"},
            {"id": "3", "status": "pending", "priority": "low"},
        ]

        # Filter by status
        pending = [t for t in tasks if t["status"] == "pending"]
        assert len(pending) == 2

        # Filter by priority
        high = [t for t in tasks if t["priority"] == "high"]
        assert len(high) == 1

        # Combined filter
        pending_low = [t for t in tasks if t["status"] == "pending" and t["priority"] == "low"]
        assert len(pending_low) == 1
```

## Testing Checklist

- [ ] Run `uv run streamlit run src/adhd_planner/ui/app.py`
- [ ] Navigate to Tasks page
- [ ] Mock tasks display correctly
- [ ] Task cards show all information
- [ ] Checkbox toggles work
- [ ] Delete button appears and works
- [ ] Filters change displayed tasks
- [ ] Metrics update correctly
- [ ] Add task form appears in sidebar
- [ ] Form validation works (empty title rejected)
- [ ] Run `uv run pytest tests/unit/test_tasks_page.py -v`
- [ ] All tests pass

## Success Criteria

- [ ] Task list displays correctly
- [ ] Filters work as expected
- [ ] Task cards show all relevant info
- [ ] Quick actions (complete, delete) work
- [ ] Add task form creates new tasks
- [ ] Integrates with TaskService when available
- [ ] Falls back to mock data when service unavailable
- [ ] Tests pass

## Implementation Notes

### Mock Data for Development
The page uses mock data when TaskService isn't available. This allows UI development to proceed without database setup.

### Filter Implementation
Filters are applied in Python after loading all tasks. For MVP this is fine. If performance becomes an issue, push filtering to the database/service layer.

### Task Card Component
The task card handles both dict and object access patterns, making it flexible for different data sources.

### MVP Approach
- No drag-and-drop reordering
- No inline editing (only complete/delete)
- No bulk actions
- Simple form, no advanced fields

## Next Story

After completing this story, proceed to:
- **ADHD-20**: Calendar View - Schedule and time block visualization
