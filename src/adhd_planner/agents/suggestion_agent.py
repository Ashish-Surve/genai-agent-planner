"""Suggestion Agent - Provides task recommendations."""

from datetime import datetime
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState


class SuggestionAgent(BaseAgent):
    """
    Suggestion Agent provides task recommendations based on current context.

    Responsibilities:
    - Analyze current context
    - Rank tasks by suitability
    - Provide recommendations
    """

    def __init__(self, llm_service, task_service, calendar_service):
        """Initialize suggestion agent."""
        super().__init__(
            name="suggestion_agent",
            description="Recommends tasks to work on",
            llm_service=llm_service,
            task_service=task_service,
            calendar_service=calendar_service,
        )

    def execute(self, state: AgentState) -> AgentState:
        """Execute suggestion logic."""
        try:
            self.log_execution(state)

            task_service = self.get_service("task_service")

            # Get incomplete tasks
            tasks = task_service.get_incomplete_tasks()

            if not tasks:
                response = "No tasks available. Create some tasks to get suggestions!"
                state = self.add_response(state, response)
                state["routing_decision"] = "END"
                return state

            # Analyze context and get suggestions
            suggestions = self._get_task_suggestions(tasks)

            # Format response
            response = self._format_response(suggestions)

            # Update state
            state = self.add_response(state, response)
            state = self.update_context(state, "task_suggestions", suggestions)
            state["routing_decision"] = "END"

            return state

        except Exception as e:
            return self.handle_error(state, e)

    def _get_task_suggestions(self, tasks: list[Any]) -> list[dict]:
        """Get task suggestions based on context."""
        suggestions = []

        # Sort by suitability
        for task in tasks[:5]:
            # MVP: Simple scoring based on deadline and priority
            urgency_score = 0
            if task.deadline:
                days_until = (task.deadline.date() - datetime.now().date()).days
                if days_until <= 1:
                    urgency_score = 10
                elif days_until <= 3:
                    urgency_score = 7
                else:
                    urgency_score = 3

            priority_score = {
                "urgent": 10,
                "high": 8,
                "medium": 5,
                "low": 2,
            }.get(task.priority.value, 5)

            total_score = (urgency_score + priority_score) / 2

            suggestion = {
                "task_id": task.id,
                "task_title": task.title,
                "duration": task.estimated_duration_minutes or 60,
                "priority": task.priority.value,
                "score": total_score,
                "reason": f"Deadline soon and {task.priority.value} priority"
                if urgency_score > 5
                else f"{task.priority.value} priority task",
            }
            suggestions.append(suggestion)

        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:3]

    def _format_response(self, suggestions: list[dict]) -> str:
        """Format suggestions response."""
        response = "💡 **Recommended Tasks:**\n\n"

        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. **{suggestion['task_title']}**\n"
            response += (
                f"   Duration: {suggestion['duration']} min | Priority: {suggestion['priority']}\n"
            )
            response += f"   Why: {suggestion['reason']}\n\n"

        return response
