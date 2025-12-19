"""Test time estimation service."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from adhd_planner.services.time_estimation_service import TimeEstimate, TimeEstimationService


@pytest.fixture
def estimation_service(test_db_session):
    """Create estimation service with test database."""
    return TimeEstimationService(test_db_session)


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service."""
    llm = Mock()
    llm.generate.return_value = "I estimate this will take 45 minutes"
    return llm


def test_time_estimate_repr(estimation_service):
    """Test TimeEstimate string representation."""
    estimate = TimeEstimate(
        estimated_minutes=30, confidence=0.8, method="default", buffer_minutes=10
    )

    repr_str = repr(estimate)
    assert "40m" in repr_str
    assert "confidence: 0.80" in repr_str
    assert "method: default" in repr_str


def test_default_estimate(estimation_service):
    """Test default estimation."""
    estimate = estimation_service._default_estimate("MEDIUM")

    assert estimate.estimated_minutes == 30
    assert estimate.method == "default"
    assert estimate.buffer_minutes > 0
    assert estimate.total_minutes > estimate.estimated_minutes


def test_default_estimate_all_energy_levels(estimation_service):
    """Test default estimates for all energy levels."""
    low = estimation_service._default_estimate("LOW")
    assert low.estimated_minutes == 15

    medium = estimation_service._default_estimate("MEDIUM")
    assert medium.estimated_minutes == 30

    high = estimation_service._default_estimate("HIGH")
    assert high.estimated_minutes == 60


def test_adhd_buffers(estimation_service):
    """Test that ADHD buffers are applied correctly."""
    # Low energy should have lower buffer
    low_buffer = estimation_service._calculate_buffer(60, "LOW")
    assert low_buffer == 12  # 20% of 60

    # High energy should have higher buffer
    high_buffer = estimation_service._calculate_buffer(60, "HIGH")
    assert high_buffer == 30  # 50% of 60

    assert high_buffer > low_buffer


def test_buffer_minimum(estimation_service):
    """Test that buffers have minimum of 5 minutes."""
    # Even very small base estimates get at least 5 min buffer
    small_buffer = estimation_service._calculate_buffer(5, "LOW")
    assert small_buffer >= 5


def test_parse_duration_from_text(estimation_service):
    """Test duration parsing from LLM responses."""
    # Various formats
    assert estimation_service._parse_duration_from_text("45 minutes") == 45
    assert estimation_service._parse_duration_from_text("1 hour") == 60
    assert estimation_service._parse_duration_from_text("2.5 hours") == 150
    assert estimation_service._parse_duration_from_text("30m") == 30
    assert estimation_service._parse_duration_from_text("2h") == 120
    assert estimation_service._parse_duration_from_text("90 mins") == 90


def test_parse_duration_fallback(estimation_service):
    """Test duration parsing fallback to any number."""
    # Should extract first number found
    assert estimation_service._parse_duration_from_text("About 45 minutes") == 45
    assert estimation_service._parse_duration_from_text("I think 30") == 30


def test_parse_duration_no_match(estimation_service):
    """Test duration parsing with no match."""
    assert estimation_service._parse_duration_from_text("no numbers here") is None
    assert estimation_service._parse_duration_from_text("") is None


def test_estimate_duration_with_llm(estimation_service, mock_llm_service):
    """Test LLM-based estimation."""
    estimation_service.llm_service = mock_llm_service

    estimate = estimation_service.estimate_duration(
        title="Write report", description="Monthly status report", energy_level="HIGH"
    )

    assert estimate.estimated_minutes == 45
    assert estimate.method == "llm"
    assert estimate.buffer_minutes > 0
    assert mock_llm_service.generate.called


def test_estimate_duration_fallback_to_default(estimation_service):
    """Test fallback to default when no LLM."""
    estimate = estimation_service.estimate_duration(
        title="New task", energy_level="MEDIUM", use_llm=False
    )

    assert estimate.method == "default"
    assert estimate.estimated_minutes == 30


def test_estimate_duration_llm_parsing_failure(estimation_service, mock_llm_service):
    """Test LLM estimation with unparseable response."""
    mock_llm_service.generate.return_value = "This is some text with no duration"
    estimation_service.llm_service = mock_llm_service

    estimate = estimation_service.estimate_duration(title="Task", energy_level="MEDIUM")

    # Should fall back to default
    assert estimate.method == "default"


def test_calculate_estimation_accuracy_no_data(estimation_service):
    """Test accuracy calculation with no completed tasks."""
    accuracy = estimation_service.calculate_estimation_accuracy()

    assert accuracy["total_tasks"] == 0
    assert accuracy["average_error_minutes"] == 0
    assert accuracy["average_error_percentage"] == 0
    assert accuracy["underestimation_rate"] == 0
    assert accuracy["overestimation_rate"] == 0


def test_calculate_estimation_accuracy_with_data(estimation_service, test_db_session):
    """Test accuracy calculation with completed tasks."""
    from adhd_planner.repositories.task_repository import TaskRepository

    repo = TaskRepository(test_db_session)

    # Create completed tasks with actual durations
    for i in range(5):
        task_data = {
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "actual_duration_minutes": 45,  # All took longer
            "estimated_energy_level": "MEDIUM",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "completed_at": datetime.utcnow(),
        }
        repo.create(task_data)

    accuracy = estimation_service.calculate_estimation_accuracy()

    assert accuracy["total_tasks"] == 5
    assert accuracy["average_error_minutes"] == 15  # Underestimated by 15m
    assert accuracy["underestimation_rate"] == 1.0  # All underestimated
    assert accuracy["overestimation_rate"] == 0.0


def test_get_user_estimation_pattern_insufficient_data(estimation_service):
    """Test pattern analysis with insufficient data."""
    pattern = estimation_service.get_user_estimation_pattern()

    assert "Not enough data" in pattern


def test_get_user_estimation_pattern_underestimate(estimation_service, test_db_session):
    """Test user pattern analysis with underestimation."""
    from adhd_planner.repositories.task_repository import TaskRepository

    repo = TaskRepository(test_db_session)

    # Create tasks where user underestimates
    for i in range(10):
        task_data = {
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "actual_duration_minutes": 45,
            "estimated_energy_level": "MEDIUM",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "completed_at": datetime.utcnow(),
        }
        repo.create(task_data)

    pattern = estimation_service.get_user_estimation_pattern()

    assert "underestimate" in pattern.lower()
    assert "buffer" in pattern.lower()


def test_get_user_estimation_pattern_overestimate(estimation_service, test_db_session):
    """Test user pattern analysis with overestimation."""
    from adhd_planner.repositories.task_repository import TaskRepository

    repo = TaskRepository(test_db_session)

    # Create tasks where user overestimates
    for i in range(10):
        task_data = {
            "title": f"Task {i}",
            "estimated_duration_minutes": 60,
            "actual_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "completed_at": datetime.utcnow(),
        }
        repo.create(task_data)

    pattern = estimation_service.get_user_estimation_pattern()

    assert "overestimate" in pattern.lower()
    assert "cautious" in pattern.lower()


def test_find_similar_tasks(estimation_service, test_db_session):
    """Test finding similar tasks."""
    from adhd_planner.repositories.task_repository import TaskRepository

    repo = TaskRepository(test_db_session)

    # Create completed tasks
    task_data = {
        "title": "Write report",
        "estimated_duration_minutes": 60,
        "actual_duration_minutes": 75,
        "estimated_energy_level": "HIGH",
        "priority": "HIGH",
        "status": "COMPLETED",
        "completed_at": datetime.utcnow(),
        "context_category": "writing",
    }
    repo.create(task_data)

    # Find similar
    similar = estimation_service._find_similar_tasks(
        title="Write documentation", context_category="writing", energy_level="HIGH"
    )

    assert len(similar) > 0
    assert any("write" in t.title.lower() for t in similar)


def test_find_similar_tasks_category_filter(estimation_service, test_db_session):
    """Test similar task filtering by category."""
    from adhd_planner.repositories.task_repository import TaskRepository

    repo = TaskRepository(test_db_session)

    # Create tasks in different categories
    writing_task = {
        "title": "Write article",
        "estimated_duration_minutes": 30,
        "actual_duration_minutes": 45,
        "estimated_energy_level": "MEDIUM",
        "priority": "MEDIUM",
        "status": "COMPLETED",
        "completed_at": datetime.utcnow(),
        "context_category": "writing",
    }
    repo.create(writing_task)

    coding_task = {
        "title": "Code feature",
        "estimated_duration_minutes": 30,
        "actual_duration_minutes": 60,
        "estimated_energy_level": "MEDIUM",
        "priority": "MEDIUM",
        "status": "COMPLETED",
        "completed_at": datetime.utcnow(),
        "context_category": "coding",
    }
    repo.create(coding_task)

    # Search for similar writing tasks
    similar = estimation_service._find_similar_tasks(
        title="Write blog post", context_category="writing", energy_level="MEDIUM"
    )

    # Should find only writing tasks
    assert all(t.context_category == "writing" for t in similar)


def test_estimate_from_history(estimation_service, test_db_session):
    """Test historical estimation."""
    from adhd_planner.repositories.task_repository import TaskRepository

    repo = TaskRepository(test_db_session)

    # Create similar completed tasks
    for _ in range(3):
        task_data = {
            "title": "Write documentation",
            "estimated_duration_minutes": 30,
            "actual_duration_minutes": 60,
            "estimated_energy_level": "HIGH",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "completed_at": datetime.utcnow(),
        }
        repo.create(task_data)

    # Estimate based on history
    estimate = estimation_service.estimate_duration(
        title="Write guide", energy_level="HIGH", use_llm=False
    )

    # Should use historical data
    assert estimate.method == "historical"
    assert estimate.estimated_minutes == 60
    assert "similar" in estimate.reasoning.lower()


def test_confidence_increases_with_more_data(estimation_service, test_db_session):
    """Test that confidence increases with more similar tasks."""
    from adhd_planner.repositories.task_repository import TaskRepository

    repo = TaskRepository(test_db_session)

    # Create 1 similar task
    for _ in range(1):
        task_data = {
            "title": "Write doc",
            "estimated_duration_minutes": 30,
            "actual_duration_minutes": 60,
            "estimated_energy_level": "HIGH",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "completed_at": datetime.utcnow(),
        }
        repo.create(task_data)

    estimate1 = estimation_service._estimate_from_history("Write test", None, "HIGH")
    conf1 = estimate1.confidence if estimate1 else 0

    # Add more similar tasks
    for _ in range(5):
        task_data = {
            "title": "Write content",
            "estimated_duration_minutes": 30,
            "actual_duration_minutes": 60,
            "estimated_energy_level": "HIGH",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "completed_at": datetime.utcnow(),
        }
        repo.create(task_data)

    estimate2 = estimation_service._estimate_from_history("Write test", None, "HIGH")
    conf2 = estimate2.confidence if estimate2 else 0

    # More tasks = higher confidence (up to 0.8 max)
    assert conf2 >= conf1
