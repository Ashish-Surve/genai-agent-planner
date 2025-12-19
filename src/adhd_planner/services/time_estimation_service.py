"""Time estimation service with ML and historical analysis."""

import re
from statistics import mean, median
from typing import Any

from sqlalchemy.orm import Session

from adhd_planner.repositories.task_repository import TaskRepository
from adhd_planner.utils.logger import get_logger

logger = get_logger("time_estimation")


class TimeEstimate:
    """Represents a time estimate with metadata."""

    def __init__(
        self,
        estimated_minutes: int,
        confidence: float,
        method: str,
        reasoning: str | None = None,
        buffer_minutes: int = 0,
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
    DEFAULT_ESTIMATES = {"LOW": 15, "MEDIUM": 30, "HIGH": 60}

    # ADHD buffer percentages by energy level
    ADHD_BUFFERS = {
        "LOW": 0.20,  # 20% buffer for low energy tasks
        "MEDIUM": 0.30,  # 30% buffer for medium energy
        "HIGH": 0.50,  # 50% buffer for high energy/focus tasks
    }

    def __init__(self, session: Session, llm_service: object | None = None):
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
        description: str | None = None,
        energy_level: str = "MEDIUM",
        context_category: str | None = None,
        use_llm: bool = True,
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
        historical_estimate = self._estimate_from_history(title, context_category, energy_level)

        if historical_estimate:
            self.logger.info(f"Using historical estimate: {historical_estimate.estimated_minutes}m")
            return historical_estimate

        # Try LLM estimation
        if use_llm and self.llm_service:
            llm_estimate = self._estimate_with_llm(title, description, energy_level)

            if llm_estimate:
                self.logger.info(f"Using LLM estimate: {llm_estimate.estimated_minutes}m")
                return llm_estimate

        # Fall back to default
        default_estimate = self._default_estimate(energy_level)
        self.logger.info(f"Using default estimate: {default_estimate.estimated_minutes}m")
        return default_estimate

    def _estimate_from_history(
        self, title: str, context_category: str | None, energy_level: str
    ) -> TimeEstimate | None:
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
        similar_tasks = self._find_similar_tasks(title, context_category, energy_level)

        if not similar_tasks:
            return None

        # Calculate average actual duration
        actual_durations = [
            t.actual_duration_minutes for t in similar_tasks if t.actual_duration_minutes
        ]

        if not actual_durations:
            return None

        median_duration = int(median(actual_durations))

        # Add buffer
        buffer = self._calculate_buffer(median_duration, energy_level)

        return TimeEstimate(
            estimated_minutes=median_duration,
            confidence=min(0.8, len(similar_tasks) * 0.2),
            method="historical",
            reasoning=f"Based on {len(similar_tasks)} similar tasks",
            buffer_minutes=buffer,
        )

    def _estimate_with_llm(
        self, title: str, description: str | None, energy_level: str
    ) -> TimeEstimate | None:
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
            # Simple prompt for estimation
            prompt = (
                f"Estimate the duration for this task in minutes:\n"
                f"Title: {title}\n"
                f"Description: {description or 'No description provided'}\n"
                f"Energy Level: {energy_level}\n\n"
                f"Provide only a number or a duration like '45 minutes' or '1 hour'."
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
                confidence=0.6,
                method="llm",
                reasoning=response.strip(),
                buffer_minutes=buffer,
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
            confidence=0.3,
            method="default",
            reasoning=f"Default estimate for {energy_level} energy tasks",
            buffer_minutes=buffer,
        )

    def _find_similar_tasks(
        self, title: str, context_category: str | None, energy_level: str, limit: int = 10
    ) -> list[Any]:
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
            completed_tasks = [t for t in completed_tasks if t.context_category == context_category]

        # Filter by energy level
        completed_tasks = [t for t in completed_tasks if t.estimated_energy_level == energy_level]

        # Simple similarity: check if any words from title appear
        title_words = set(title.lower().split())
        similar_tasks = []

        for task in completed_tasks:
            task_words = set(task.title.lower().split())
            common_words = title_words & task_words

            if common_words:
                similar_tasks.append(task)

        return similar_tasks[:limit]

    def _calculate_buffer(self, base_minutes: int, energy_level: str) -> int:
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

    def _parse_duration_from_text(self, text: str) -> int | None:
        """
        Parse duration from LLM response text.

        Args:
            text: LLM response

        Returns:
            Duration in minutes or None
        """
        # Look for patterns like "30 minutes", "1 hour", "45m", "2h"
        patterns = [
            r"(\d+)\s*minutes?",
            r"(\d+)\s*mins?",
            r"(\d+)\s*m\b",
            r"(\d+\.?\d*)\s*hours?",
            r"(\d+\.?\d*)\s*h\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1))

                # Convert hours to minutes
                if "hour" in pattern or "h" in pattern:
                    value *= 60

                return int(value)

        # If no pattern matched, look for any number
        match = re.search(r"\b(\d+)\b", text)
        if match:
            return int(match.group(1))

        return None

    def calculate_estimation_accuracy(self) -> dict[str, Any]:
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
                "overestimation_rate": 0,
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
        avg_error_pct = (
            mean(
                [
                    abs(actual - estimated) / estimated * 100
                    for task in completed_tasks
                    for estimated, actual in [
                        (task.estimated_duration_minutes, task.actual_duration_minutes)
                    ]
                    if estimated > 0
                ]
            )
            if completed_tasks
            else 0
        )

        return {
            "total_tasks": len(completed_tasks),
            "average_error_minutes": int(avg_error),
            "average_error_percentage": round(avg_error_pct, 1),
            "underestimation_rate": underestimations / len(completed_tasks),
            "overestimation_rate": overestimations / len(completed_tasks),
            "median_error_minutes": int(median(errors)),
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
