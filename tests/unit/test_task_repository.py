"""Test task repository."""

import pytest
from datetime import datetime, timedelta
from src.repositories.task_repository import TaskRepository


@pytest.fixture
def task_repo(test_db_session):
    """Create task repository."""
    return TaskRepository(test_db_session)


def test_find_by_status(task_repo):
    """Test finding tasks by status."""
    task_repo.create({
        "title": "Not started task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "status": "NOT_STARTED"
    })
    task_repo.create({
        "title": "In progress task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "status": "IN_PROGRESS"
    })

    not_started = task_repo.find_by_status("NOT_STARTED")
    assert len(not_started) == 1
    assert not_started[0].title == "Not started task"


def test_find_by_priority(task_repo):
    """Test finding tasks by priority."""
    task_repo.create({
        "title": "Urgent task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "URGENT"
    })
    task_repo.create({
        "title": "Low priority task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "LOW"
    })

    urgent = task_repo.find_by_priority("URGENT")
    assert len(urgent) == 1
    assert urgent[0].title == "Urgent task"


def test_find_overdue(task_repo):
    """Test finding overdue tasks."""
    past = datetime.utcnow() - timedelta(days=1)
    future = datetime.utcnow() + timedelta(days=1)

    task_repo.create({
        "title": "Overdue task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "deadline": past
    })
    task_repo.create({
        "title": "Future task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "deadline": future
    })

    overdue = task_repo.find_overdue()
    assert len(overdue) == 1
    assert overdue[0].title == "Overdue task"


def test_find_due_soon(task_repo):
    """Test finding tasks due soon."""
    soon = datetime.utcnow() + timedelta(hours=12)
    far = datetime.utcnow() + timedelta(days=2)

    task_repo.create({
        "title": "Due soon task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "deadline": soon
    })
    task_repo.create({
        "title": "Due later task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "deadline": far
    })

    due_soon = task_repo.find_due_soon(hours=24)
    assert len(due_soon) == 1
    assert due_soon[0].title == "Due soon task"


def test_find_by_energy_level(task_repo):
    """Test finding tasks by energy level."""
    task_repo.create({
        "title": "High energy task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "HIGH",
        "priority": "HIGH"
    })
    task_repo.create({
        "title": "Low energy task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "LOW",
        "priority": "HIGH"
    })

    high_energy = task_repo.find_by_energy_level("HIGH")
    assert len(high_energy) == 1
    assert high_energy[0].title == "High energy task"


def test_find_by_context(task_repo):
    """Test finding tasks by context."""
    task_repo.create({
        "title": "Work task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "context_category": "WORK"
    })
    task_repo.create({
        "title": "Personal task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "context_category": "PERSONAL"
    })

    work_tasks = task_repo.find_by_context("WORK")
    assert len(work_tasks) == 1
    assert work_tasks[0].title == "Work task"


def test_find_requiring_focus(task_repo):
    """Test finding tasks requiring focus."""
    task_repo.create({
        "title": "Focus task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "HIGH",
        "priority": "HIGH",
        "requires_focus": True,
        "status": "NOT_STARTED"
    })
    task_repo.create({
        "title": "Easy task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "LOW",
        "priority": "LOW",
        "requires_focus": False,
        "status": "NOT_STARTED"
    })

    focus_tasks = task_repo.find_requiring_focus()
    assert len(focus_tasks) == 1
    assert focus_tasks[0].title == "Focus task"


def test_find_completed_with_durations(task_repo):
    """Test finding completed tasks with durations."""
    task_repo.create({
        "title": "Completed task",
        "estimated_duration_minutes": 30,
        "actual_duration_minutes": 45,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "status": "COMPLETED"
    })
    task_repo.create({
        "title": "Incomplete task",
        "estimated_duration_minutes": 30,
        "actual_duration_minutes": None,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "status": "IN_PROGRESS"
    })

    completed = task_repo.find_completed_with_durations()
    assert len(completed) == 1
    assert completed[0].actual_duration_minutes == 45


def test_find_pending_sync(task_repo):
    """Test finding tasks pending sync."""
    task_repo.create({
        "title": "Pending sync task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "sync_enabled": True,
        "sync_status": "PENDING"
    })
    task_repo.create({
        "title": "Synced task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "sync_enabled": True,
        "sync_status": "SYNCED"
    })

    pending = task_repo.find_pending_sync()
    assert len(pending) == 1
    assert pending[0].title == "Pending sync task"


def test_search_by_title(task_repo):
    """Test searching tasks by title."""
    task_repo.create({
        "title": "Research ADHD strategies",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH"
    })
    task_repo.create({
        "title": "Complete project",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH"
    })

    results = task_repo.search_by_title("ADHD")
    assert len(results) == 1
    assert results[0].title == "Research ADHD strategies"


def test_get_statistics(task_repo):
    """Test getting task statistics."""
    for i in range(3):
        task_repo.create({
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH",
            "status": "NOT_STARTED"
        })

    task_repo.create({
        "title": "Completed task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
        "status": "COMPLETED"
    })

    stats = task_repo.get_statistics()
    assert stats["total"] == 4
    assert stats["not_started"] == 3
    assert stats["completed"] == 1
