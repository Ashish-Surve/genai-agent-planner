"""Planning Agent - Handles task creation and planning."""

import json
from datetime import datetime
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from models.task import TaskCreate
from models.enums import Priority, EnergyLevel
from adhd_planner.utils.prompts.planning_prompts import (
    PLANNING_SYSTEM_PROMPT,
    get_task_extraction_prompt,
)


class PlanningAgent(BaseAgent):
    """
    Planning Agent handles task creation and modification.

    Responsibilities:
    - Extract task details from natural language
    - Estimate time and energy requirements
    - Create tasks
    """

    def __init__(
        self,
        llm_service,
        task_service,
    ):
        """Initialize planning agent."""
        super().__init__(
            name="planning_agent",
            description="Creates and modifies tasks from natural language",
            llm_service=llm_service,
            task_service=task_service,
        )

    def execute(self, state: AgentState) -> AgentState:
        """Execute planning logic."""
        try:
            self.log_execution(state)

            user_input = state["user_input"]

            # Extract task details from natural language
            task_data = self._extract_task_details(user_input)

            # Check if clarification is needed
            if task_data.get("needs_clarification"):
                question = task_data.get("clarification_question")
                state = self.add_response(state, question)
                state["routing_decision"] = "END"
                return state

            # Create task using Task Service
            task = self._create_task(task_data)

            # Format response
            response = self._format_response(task)

            # Update state
            state = self.add_response(state, response)
            state = self.update_context(state, "created_task", task.model_dump())
            state["routing_decision"] = "END"

            return state

        except Exception as e:
            return self.handle_error(state, e)

    def _extract_task_details(self, user_input: str) -> dict[str, Any]:
        """Extract task details from natural language."""
        llm_service = self.get_service("llm_service")

        context = {"current_time": datetime.now().isoformat()}
        prompt = get_task_extraction_prompt(user_input, context)

        response = llm_service.generate(
            prompt=prompt,
            system_prompt=PLANNING_SYSTEM_PROMPT,
            temperature=0.3,
        )

        task_data = json.loads(response)
        self.logger.debug(f"Extracted task data: {task_data}")
        return task_data

    def _create_task(self, task_data: dict[str, Any]) -> Any:
        """Create task using Task Service."""
        task_service = self.get_service("task_service")

        task_create = TaskCreate(
            title=task_data["title"],
            description=task_data.get("description"),
            estimated_duration_minutes=task_data.get("estimated_duration_minutes"),
            priority=Priority[task_data.get("priority", "medium").upper()],
            energy_level=EnergyLevel[task_data.get("energy_level", "medium").upper()],
            deadline=datetime.fromisoformat(task_data["deadline"])
            if task_data.get("deadline")
            else None,
        )

        task = task_service.create_task(task_create)
        self.logger.info(f"Created task: {task.title} (ID: {task.id})")
        return task

    def _format_response(self, task: Any) -> str:
        """Format user-friendly response."""
        response = f"✅ Created task: **{task.title}**\n\n"

        if task.description:
            response += f"Description: {task.description}\n"

        if task.estimated_duration_minutes:
            response += f"Duration: {task.estimated_duration_minutes} minutes\n"

        response += f"Priority: {task.priority.value}\n"
        response += f"Energy: {task.energy_level.value}\n"

        if task.deadline:
            response += f"Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"

        return response
