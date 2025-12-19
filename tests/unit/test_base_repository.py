"""Test base repository."""

import pytest

from adhd_planner.database.schema import TaskModel
from adhd_planner.repositories.base_repository import BaseRepository


@pytest.fixture
def task_repository(test_db_session):
    """Create task repository for testing."""
    return BaseRepository(TaskModel, test_db_session)


def test_create(task_repository):
    """Test creating an entity."""
    data = {
        "title": "Test task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
    }

    task = task_repository.create(data)

    assert task.id is not None
    assert task.title == "Test task"
    assert task.estimated_duration_minutes == 30


def test_get_by_id(task_repository):
    """Test getting entity by ID."""
    # Create task
    data = {
        "title": "Test task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH",
    }
    task = task_repository.create(data)

    # Get by ID
    retrieved = task_repository.get_by_id(task.id)

    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.title == task.title


def test_get_by_id_not_found(task_repository):
    """Test getting non-existent entity."""
    result = task_repository.get_by_id("non-existent-id")
    assert result is None


def test_get_all(task_repository):
    """Test getting all entities."""
    # Create multiple tasks
    for i in range(5):
        task_repository.create(
            {
                "title": f"Task {i}",
                "estimated_duration_minutes": 30,
                "estimated_energy_level": "MEDIUM",
                "priority": "HIGH",
            }
        )

    # Get all
    tasks = task_repository.get_all()
    assert len(tasks) == 5


def test_get_all_with_pagination(task_repository):
    """Test pagination."""
    # Create tasks
    for i in range(10):
        task_repository.create(
            {
                "title": f"Task {i}",
                "estimated_duration_minutes": 30,
                "estimated_energy_level": "MEDIUM",
                "priority": "HIGH",
            }
        )

    # Get with limit
    tasks = task_repository.get_all(limit=5)
    assert len(tasks) == 5

    # Get with offset
    tasks = task_repository.get_all(limit=5, offset=5)
    assert len(tasks) == 5


def test_update(task_repository):
    """Test updating an entity."""
    # Create task
    task = task_repository.create(
        {
            "title": "Original title",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH",
        }
    )

    # Update
    updated = task_repository.update(
        task.id, {"title": "Updated title", "estimated_duration_minutes": 45}
    )

    assert updated.title == "Updated title"
    assert updated.estimated_duration_minutes == 45


def test_update_not_found(task_repository):
    """Test updating non-existent entity."""
    result = task_repository.update("non-existent-id", {"title": "New"})
    assert result is None


def test_delete(task_repository):
    """Test deleting an entity."""
    # Create task
    task = task_repository.create(
        {
            "title": "Test task",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH",
        }
    )

    # Delete
    success = task_repository.delete(task.id)
    assert success is True

    # Verify deleted
    result = task_repository.get_by_id(task.id)
    assert result is None


def test_delete_not_found(task_repository):
    """Test deleting non-existent entity."""
    success = task_repository.delete("non-existent-id")
    assert success is False


def test_find_by_filters(task_repository):
    """Test finding entities by filters."""
    # Create tasks with different priorities
    task_repository.create(
        {
            "title": "High priority task",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH",
        }
    )
    task_repository.create(
        {
            "title": "Low priority task",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "LOW",
        }
    )

    # Find by filter
    high_priority = task_repository.find_by_filters({"priority": "HIGH"})
    assert len(high_priority) == 1
    assert high_priority[0].title == "High priority task"


def test_count(task_repository):
    """Test counting entities."""
    # Create tasks
    for i in range(7):
        task_repository.create(
            {
                "title": f"Task {i}",
                "estimated_duration_minutes": 30,
                "estimated_energy_level": "MEDIUM",
                "priority": "HIGH",
            }
        )

    # Count all
    count = task_repository.count()
    assert count == 7

    # Count with filter
    count = task_repository.count({"priority": "HIGH"})
    assert count == 7


def test_exists(task_repository):
    """Test checking if entity exists."""
    # Create task
    task = task_repository.create(
        {
            "title": "Test task",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH",
        }
    )

    # Check exists
    assert task_repository.exists(task.id) is True
    assert task_repository.exists("non-existent-id") is False


def test_bulk_create(task_repository):
    """Test bulk creation."""
    data_list = [
        {
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH",
        }
        for i in range(5)
    ]

    tasks = task_repository.bulk_create(data_list)

    assert len(tasks) == 5
    assert all(task.id is not None for task in tasks)


def test_bulk_delete(task_repository):
    """Test bulk deletion."""
    # Create tasks
    tasks = task_repository.bulk_create(
        [
            {
                "title": f"Task {i}",
                "estimated_duration_minutes": 30,
                "estimated_energy_level": "MEDIUM",
                "priority": "HIGH",
            }
            for i in range(5)
        ]
    )

    # Get IDs
    task_ids = [task.id for task in tasks]

    # Bulk delete
    deleted_count = task_repository.bulk_delete(task_ids)

    assert deleted_count == 5

    # Verify all deleted
    for task_id in task_ids:
        assert task_repository.get_by_id(task_id) is None
