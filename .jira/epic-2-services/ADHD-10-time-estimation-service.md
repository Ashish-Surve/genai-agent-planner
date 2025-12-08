# ADHD-10: Time Estimation Service

## Story Information

- **Epic**: Core Services
- **Story Points**: 2
- **Estimated Time**: 2 hours
- **Prerequisites**: ADHD-7 (LLM Service), ADHD-8 (Task Service)
- **Status**: 📋 Not Started

## Description

Implement the Time Estimation Service that combines historical data analysis with LLM-based estimation to predict task durations. This service learns from actual completion times and helps users with ADHD overcome time blindness by providing realistic estimates with appropriate buffers.

## Goals

1. Analyze historical task completion data
2. Use LLM for intelligent time estimation
3. Track estimation accuracy over time
4. Learn from actual vs estimated durations
5. Provide confidence scores for estimates
6. Add ADHD-friendly buffers automatically
7. Support task similarity matching

## Acceptance Criteria

- [ ] Historical analysis works for completed tasks
- [ ] LLM-based estimation provides reasonable estimates
- [ ] Accuracy tracking calculates correct metrics
- [ ] Service learns from actual durations
- [ ] Confidence scores are meaningful
- [ ] Buffers added based on task type
- [ ] All operations logged
- [ ] Unit tests pass

## Files to Create

```
src/services/time_estimation_service.py     # Main estimation service
tests/unit/test_time_estimation_service.py  # Service tests
```

## Implementation Steps

### Step 1: Time Estimation Service (60 min)

**File**: `src/services/time_estimation_service.py`

```python
"""Time estimation service with ML and historical analysis."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from statistics import mean, median

from src.services.llm_service import LLMService
from src.repositories.task_repository import TaskRepository
from src.models.task import Task, EnergyLevel
from src.utils.logger import get_logger
from src.utils.prompts import ESTIMATE_DURATION_PROMPT, format_prompt

logger = get_logger("time_estimation")


class TimeEstimate:
    """Represents a time estimate with metadata."""

    def __init__(
        self,
        estimated_minutes: int,
        confidence: float,
        method: str,
        reasoning: Optional[str] = None,
        buffer_minutes: int = 0
    ):
        self.estimated_minutes = estimated_minutes
        self.confidence = confidence  # 0.0 - 1.0
        self.method = method  # "historical", "llm", "default"
        self.reasoning = reasoning
        self.buffer_minutes = buffer_minutes
        self.total_minutes = estimated_minutes + buffer_minutes

    def __repr__(self) -> str:
        return (
            f"TimeEstimate({self.total_minutes}m "
            f"[base: {self.estimated_minutes}m + buffer: {self.buffer_minutes}m], "
            f"confidence: {self.confidence:.2f}, method: {self.method})"
        )


class TimeEstimationService:
    """Service for intelligent time estimation."""

    # Default estimates by energy level (in minutes)
    DEFAULT_ESTIMATES = {
        "LOW": 15,
        "MEDIUM": 30,
        "HIGH": 60
    }

    # ADHD buffer percentages by energy level
    ADHD_BUFFERS = {
        "LOW": 0.20,    # 20% buffer for low energy tasks
        "MEDIUM": 0.30,  # 30% buffer for medium energy
        "HIGH": 0.50     # 50% buffer for high energy/focus tasks
    }

    def __init__(
        self,
        session: Session,
        llm_service: Optional[LLMService] = None
    ):
        """
        Initialize time estimation service.

        Args:
            session: Database session
            llm_service: Optional LLM service for AI-based estimation
        """
        self.session = session
        self.task_repository = TaskRepository(session)
        self.llm_service = llm_service
        self.logger = logger

    def estimate_duration(
        self,
        title: str,
        description: Optional[str] = None,
        energy_level: str = "MEDIUM",
        context_category: Optional[str] = None,
        use_llm: bool = True
    ) -> TimeEstimate:
        """
        Estimate task duration using multiple methods.

        Args:
            title: Task title
            description: Optional description
            energy_level: Required energy level
            context_category: Task category
            use_llm: Whether to use LLM for estimation

        Returns:
            TimeEstimate with duration and confidence
        """
        self.logger.debug(f"Estimating duration for: {title}")

        # Try historical analysis first
        historical_estimate = self._estimate_from_history(
            title,
            context_category,
            energy_level
        )

        if historical_estimate:
            self.logger.info(
                f"Using historical estimate: {historical_estimate.estimated_minutes}m"
            )
            return historical_estimate

        # Try LLM estimation
        if use_llm and self.llm_service:
            llm_estimate = self._estimate_with_llm(
                title,
                description,
                energy_level
            )

            if llm_estimate:
                self.logger.info(
                    f"Using LLM estimate: {llm_estimate.estimated_minutes}m"
                )
                return llm_estimate

        # Fall back to default
        default_estimate = self._default_estimate(energy_level)
        self.logger.info(
            f"Using default estimate: {default_estimate.estimated_minutes}m"
        )
        return default_estimate

    def _estimate_from_history(
        self,
        title: str,
        context_category: Optional[str],
        energy_level: str
    ) -> Optional[TimeEstimate]:
        """
        Estimate based on similar completed tasks.

        Args:
            title: Task title
            context_category: Task category
            energy_level: Required energy level

        Returns:
            TimeEstimate if similar tasks found, else None
        """
        # Find similar completed tasks
        similar_tasks = self._find_similar_tasks(
            title,
            context_category,
            energy_level
        )

        if not similar_tasks:
            return None

        # Calculate average actual duration
        actual_durations = [
            t.actual_duration_minutes
            for t in similar_tasks
            if t.actual_duration_minutes
        ]

        if not actual_durations:
            return None

        avg_duration = int(mean(actual_durations))
        median_duration = int(median(actual_durations))

        # Use median to avoid outliers
        base_estimate = median_duration

        # Add buffer
        buffer = self._calculate_buffer(base_estimate, energy_level)

        return TimeEstimate(
            estimated_minutes=base_estimate,
            confidence=min(0.8, len(similar_tasks) * 0.2),  # More tasks = higher confidence
            method="historical",
            reasoning=f"Based on {len(similar_tasks)} similar tasks",
            buffer_minutes=buffer
        )

    def _estimate_with_llm(
        self,
        title: str,
        description: Optional[str],
        energy_level: str
    ) -> Optional[TimeEstimate]:
        """
        Estimate using LLM.

        Args:
            title: Task title
            description: Optional description
            energy_level: Required energy level

        Returns:
            TimeEstimate from LLM or None if failed
        """
        try:
            prompt = format_prompt(
                ESTIMATE_DURATION_PROMPT,
                task_title=title,
                task_description=description or "No description provided"
            )

            response = self.llm_service.generate(prompt)

            # Parse response - expect a number
            estimated_minutes = self._parse_duration_from_text(response)

            if not estimated_minutes:
                self.logger.warning("Could not parse LLM estimate")
                return None

            # Add buffer
            buffer = self._calculate_buffer(estimated_minutes, energy_level)

            return TimeEstimate(
                estimated_minutes=estimated_minutes,
                confidence=0.6,  # Medium confidence for LLM
                method="llm",
                reasoning=response.strip(),
                buffer_minutes=buffer
            )

        except Exception as e:
            self.logger.error(f"LLM estimation failed: {e}")
            return None

    def _default_estimate(self, energy_level: str) -> TimeEstimate:
        """
        Provide default estimate based on energy level.

        Args:
            energy_level: Required energy level

        Returns:
            Default TimeEstimate
        """
        base_estimate = self.DEFAULT_ESTIMATES.get(energy_level, 30)
        buffer = self._calculate_buffer(base_estimate, energy_level)

        return TimeEstimate(
            estimated_minutes=base_estimate,
            confidence=0.3,  # Low confidence for default
            method="default",
            reasoning=f"Default estimate for {energy_level} energy tasks",
            buffer_minutes=buffer
        )

    def _find_similar_tasks(
        self,
        title: str,
        context_category: Optional[str],
        energy_level: str,
        limit: int = 10
    ) -> List[Task]:
        """
        Find similar completed tasks.

        Args:
            title: Task title to match
            context_category: Optional category
            energy_level: Energy level
            limit: Maximum tasks to return

        Returns:
            List of similar tasks
        """
        # Get all completed tasks with actual durations
        completed_tasks = self.task_repository.find_completed_with_durations()

        # Filter by category if provided
        if context_category:
            completed_tasks = [
                t for t in completed_tasks
                if t.context_category == context_category
            ]

        # Filter by energy level
        completed_tasks = [
            t for t in completed_tasks
            if t.estimated_energy_level == energy_level
        ]

        # Simple similarity: check if any words from title appear
        title_words = set(title.lower().split())
        similar_tasks = []

        for task in completed_tasks:
            task_words = set(task.title.lower().split())
            common_words = title_words & task_words

            if common_words:
                similar_tasks.append(task)

        return similar_tasks[:limit]

    def _calculate_buffer(
        self,
        base_minutes: int,
        energy_level: str
    ) -> int:
        """
        Calculate ADHD-friendly buffer time.

        Args:
            base_minutes: Base estimate
            energy_level: Required energy level

        Returns:
            Buffer time in minutes
        """
        buffer_percentage = self.ADHD_BUFFERS.get(energy_level, 0.30)
        buffer = int(base_minutes * buffer_percentage)

        # Minimum 5 minute buffer
        return max(5, buffer)

    def _parse_duration_from_text(self, text: str) -> Optional[int]:
        """
        Parse duration from LLM response text.

        Args:
            text: LLM response

        Returns:
            Duration in minutes or None
        """
        import re

        # Look for patterns like "30 minutes", "1 hour", "45m", "2h"
        patterns = [
            r'(\d+)\s*minutes?',
            r'(\d+)\s*mins?',
            r'(\d+)\s*m\b',
            r'(\d+\.?\d*)\s*hours?',
            r'(\d+\.?\d*)\s*h\b'
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1))

                # Convert hours to minutes
                if 'hour' in pattern or 'h' in pattern:
                    value *= 60

                return int(value)

        # If no pattern matched, look for any number
        match = re.search(r'\b(\d+)\b', text)
        if match:
            return int(match.group(1))

        return None

    def calculate_estimation_accuracy(self) -> Dict[str, Any]:
        """
        Calculate estimation accuracy metrics.

        Returns:
            Dictionary with accuracy statistics
        """
        completed_tasks = self.task_repository.find_completed_with_durations()

        if not completed_tasks:
            return {
                "total_tasks": 0,
                "average_error_minutes": 0,
                "average_error_percentage": 0,
                "underestimation_rate": 0,
                "overestimation_rate": 0
            }

        errors = []
        underestimations = 0
        overestimations = 0

        for task in completed_tasks:
            estimated = task.estimated_duration_minutes
            actual = task.actual_duration_minutes

            error = actual - estimated
            errors.append(error)

            if error > 0:
                underestimations += 1
            elif error < 0:
                overestimations += 1

        avg_error = mean(errors)
        avg_error_pct = mean([
            abs(actual - estimated) / estimated * 100
            for task in completed_tasks
            for estimated, actual in [(task.estimated_duration_minutes, task.actual_duration_minutes)]
            if estimated > 0
        ]) if completed_tasks else 0

        return {
            "total_tasks": len(completed_tasks),
            "average_error_minutes": int(avg_error),
            "average_error_percentage": round(avg_error_pct, 1),
            "underestimation_rate": underestimations / len(completed_tasks),
            "overestimation_rate": overestimations / len(completed_tasks),
            "median_error_minutes": int(median(errors))
        }

    def get_user_estimation_pattern(self) -> str:
        """
        Analyze user's estimation patterns.

        Returns:
            Human-readable pattern description
        """
        accuracy = self.calculate_estimation_accuracy()

        if accuracy["total_tasks"] < 5:
            return "Not enough data yet - complete more tasks to see patterns"

        avg_error = accuracy["average_error_minutes"]
        underestimate_rate = accuracy["underestimation_rate"]

        if underestimate_rate > 0.7:
            return (
                f"You tend to underestimate tasks by ~{abs(avg_error)} minutes. "
                "This is common with ADHD - we're adding buffers to help!"
            )
        elif underestimate_rate < 0.3:
            return (
                f"You tend to overestimate tasks by ~{abs(avg_error)} minutes. "
                "You're being cautious - that's great for planning!"
            )
        else:
            return (
                f"Your estimates are fairly balanced (±{abs(avg_error)} minutes). "
                "Keep tracking to improve accuracy!"
            )
```

### Step 2: Unit Tests (40 min)

**File**: `tests/unit/test_time_estimation_service.py`

```python
"""Test time estimation service."""

import pytest
from unittest.mock import Mock
from src.services.time_estimation_service import (
    TimeEstimationService,
    TimeEstimate
)
from src.models.task import Task


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


def test_default_estimate(estimation_service):
    """Test default estimation."""
    estimate = estimation_service._default_estimate("MEDIUM")

    assert estimate.estimated_minutes == 30
    assert estimate.method == "default"
    assert estimate.buffer_minutes > 0
    assert estimate.total_minutes > estimate.estimated_minutes


def test_adhd_buffers(estimation_service):
    """Test that ADHD buffers are applied correctly."""
    # Low energy should have lower buffer
    low_buffer = estimation_service._calculate_buffer(60, "LOW")
    assert low_buffer == 12  # 20% of 60

    # High energy should have higher buffer
    high_buffer = estimation_service._calculate_buffer(60, "HIGH")
    assert high_buffer == 30  # 50% of 60

    assert high_buffer > low_buffer


def test_parse_duration_from_text(estimation_service):
    """Test duration parsing from LLM responses."""
    # Various formats
    assert estimation_service._parse_duration_from_text("45 minutes") == 45
    assert estimation_service._parse_duration_from_text("1 hour") == 60
    assert estimation_service._parse_duration_from_text("2.5 hours") == 150
    assert estimation_service._parse_duration_from_text("30m") == 30
    assert estimation_service._parse_duration_from_text("1h 30m") == 60  # Gets first match


def test_estimate_duration_with_llm(estimation_service, mock_llm_service):
    """Test LLM-based estimation."""
    estimation_service.llm_service = mock_llm_service

    estimate = estimation_service.estimate_duration(
        title="Write report",
        description="Monthly status report",
        energy_level="HIGH"
    )

    assert estimate.estimated_minutes == 45
    assert estimate.method == "llm"
    assert estimate.buffer_minutes > 0
    assert mock_llm_service.generate.called


def test_estimate_duration_fallback_to_default(estimation_service):
    """Test fallback to default when no LLM."""
    estimate = estimation_service.estimate_duration(
        title="New task",
        energy_level="MEDIUM",
        use_llm=False
    )

    assert estimate.method == "default"
    assert estimate.estimated_minutes == 30


def test_calculation_accuracy_no_data(estimation_service):
    """Test accuracy calculation with no completed tasks."""
    accuracy = estimation_service.calculate_estimation_accuracy()

    assert accuracy["total_tasks"] == 0
    assert accuracy["average_error_minutes"] == 0


def test_calculation_accuracy_with_data(
    estimation_service,
    test_db_session
):
    """Test accuracy calculation with completed tasks."""
    from src.repositories.task_repository import TaskRepository
    from datetime import datetime

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
            "completed_at": datetime.utcnow()
        }
        repo.create(task_data)

    accuracy = estimation_service.calculate_estimation_accuracy()

    assert accuracy["total_tasks"] == 5
    assert accuracy["average_error_minutes"] == 15  # Underestimated by 15m
    assert accuracy["underestimation_rate"] == 1.0  # All underestimated


def test_get_user_estimation_pattern(estimation_service, test_db_session):
    """Test user pattern analysis."""
    from src.repositories.task_repository import TaskRepository
    from datetime import datetime

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
            "completed_at": datetime.utcnow()
        }
        repo.create(task_data)

    pattern = estimation_service.get_user_estimation_pattern()

    assert "underestimate" in pattern.lower()
    assert "buffer" in pattern.lower()


def test_find_similar_tasks(estimation_service, test_db_session):
    """Test finding similar tasks."""
    from src.repositories.task_repository import TaskRepository
    from datetime import datetime

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
        "context_category": "writing"
    }
    repo.create(task_data)

    # Find similar
    similar = estimation_service._find_similar_tasks(
        title="Write documentation",
        context_category="writing",
        energy_level="HIGH"
    )

    assert len(similar) > 0
    assert any("write" in t.title.lower() for t in similar)
```

## Testing Checklist

```bash
# 1. Run unit tests
uv run pytest tests/unit/test_time_estimation_service.py -v

# 2. Test duration estimation
uv run python -c "
from src.database.connection import get_db
from src.services.time_estimation_service import TimeEstimationService

db = get_db()
with db.get_session() as session:
    service = TimeEstimationService(session)

    estimate = service.estimate_duration(
        title='Write report',
        description='Monthly status update',
        energy_level='HIGH',
        use_llm=False
    )

    print(f'Estimate: {estimate}')
"

# 3. Test accuracy tracking
uv run python -c "
from src.database.connection import get_db
from src.services.time_estimation_service import TimeEstimationService

db = get_db()
with db.get_session() as session:
    service = TimeEstimationService(session)

    accuracy = service.calculate_estimation_accuracy()
    print(f'Accuracy: {accuracy}')

    pattern = service.get_user_estimation_pattern()
    print(f'Pattern: {pattern}')
"

# 4. Run all tests
uv run pytest tests/unit/ -v

# 5. Code quality
uv run ruff check src/services/time_estimation_service.py
uv run black --check src/services/
```

## Success Criteria

- ✅ Historical analysis works correctly
- ✅ LLM estimation provides reasonable results
- ✅ Accuracy tracking calculates correct metrics
- ✅ Buffers added appropriately
- ✅ Confidence scores are meaningful
- ✅ All unit tests pass
- ✅ Code quality checks pass

## Common Issues & Solutions

### Issue: LLM returns non-numeric response
**Solution**: Robust parsing with multiple pattern matching, fallback to default

### Issue: Accuracy metrics skewed by outliers
**Solution**: Use median in addition to mean, consider removing extreme outliers

### Issue: Similar task matching too strict/loose
**Solution**: Adjust similarity algorithm, consider using embeddings for better matching

## Next Story

Once this story is complete, move to:
**[ADHD-11: LangGraph State & Base Agent](../epic-3-agents/ADHD-11-langgraph-state-base-agent.md)**

## Notes

- Time estimation is critical for ADHD users who struggle with time blindness
- Buffers are essential - better to overestimate than underestimate
- Learning from actual durations improves estimates over time
- LLM can provide context-aware estimates when historical data is sparse
- Confidence scores help users trust (or question) estimates
- Pattern analysis helps users understand their estimation biases