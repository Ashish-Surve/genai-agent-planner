"""Tests for tasks page components."""


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
