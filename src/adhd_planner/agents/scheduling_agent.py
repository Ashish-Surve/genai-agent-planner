"""Scheduling Agent - Generates ADHD-friendly schedules."""

from datetime import datetime, timedelta
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState


class SchedulingAgent(BaseAgent):
    """
    Scheduling Agent generates ADHD-friendly daily and weekly schedules.

    Responsibilities:
    - Generate optimized schedules
    - Apply ADHD-friendly rules
    - Provide schedule options
    """

    def __init__(self, llm_service, task_service, calendar_service):
        """Initialize scheduling agent."""
        super().__init__(
            name="scheduling_agent",
            description="Generates ADHD-friendly schedules",
            llm_service=llm_service,
            task_service=task_service,
            calendar_service=calendar_service,
        )

    def execute(self, state: AgentState) -> AgentState:
        """Execute scheduling logic."""
        try:
            self.log_execution(state)

            task_service = self.get_service("task_service")

            # Get incomplete tasks
            tasks = task_service.get_incomplete_tasks()

            if not tasks:
                response = "No tasks to schedule. Create some tasks first!"
                state = self.add_response(state, response)
                state["routing_decision"] = "END"
                return state

            # Generate schedule suggestions
            suggestions = self._generate_schedule_suggestions(tasks, state)

            # Format response
            response = self._format_response(suggestions)

            # Update state
            state = self.add_response(state, response)
            state = self.update_context(state, "schedule_suggestions", suggestions)
            state["routing_decision"] = "END"

            return state

        except Exception as e:
            return self.handle_error(state, e)

    def _generate_schedule_suggestions(self, tasks: list[Any], state: AgentState) -> list[dict]:
        """Generate schedule suggestions using ADHD-friendly rules."""
        # MVP: Simple suggestions based on priority and energy
        suggestions = []

        # Sort by priority and deadline
        # TaskModel stores priority and estimated_energy_level as strings, not enums
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                -{"URGENT": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(str(t.priority).upper(), 1),
                t.deadline or datetime.now() + timedelta(days=365),
            ),
        )

        for i, task in enumerate(sorted_tasks[:5]):
            suggestion = {
                "task_id": task.id,
                "task_title": task.title,
                "duration": task.estimated_duration_minutes or 60,
                "priority": str(task.priority),
                "position": i + 1,
                "reasoning": f"Priority: {task.priority}, Energy: {task.estimated_energy_level}",
            }
            suggestions.append(suggestion)

        return suggestions

    def _format_response(self, suggestions: list[dict]) -> str:
        """Format schedule suggestions response."""
        response = "📅 **Suggested Schedule:**\n\n"

        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. **{suggestion['task_title']}**\n"
            response += (
                f"   Duration: {suggestion['duration']} min | Priority: {suggestion['priority']}\n"
            )
            response += f"   Reasoning: {suggestion['reasoning']}\n\n"

        return response
