"""Scheduling Agent - Generates ADHD-friendly schedules with multi-turn confirmation."""

from datetime import datetime, timedelta
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from adhd_planner.models.enums import BlockType


class SchedulingAgent(BaseAgent):
    """
    Scheduling Agent generates ADHD-friendly daily and weekly schedules.

    Responsibilities:
    - Generate optimized schedules
    - Apply ADHD-friendly rules
    - Provide schedule options
    - Handle multi-turn confirmation flow
    - Create time blocks upon user confirmation
    """

    # Keywords indicating user confirmation
    CONFIRM_KEYWORDS = [
        "yes",
        "confirm",
        "schedule",
        "do it",
        "ok",
        "sure",
        "go ahead",
        "sounds good",
        "let's do it",
    ]
    CANCEL_KEYWORDS = ["no", "cancel", "nevermind", "never mind", "stop", "don't"]
    MODIFY_KEYWORDS = ["change", "modify", "different", "adjust", "skip", "remove"]

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
        """Execute scheduling logic with multi-turn support."""
        try:
            self.log_execution(state)

            user_input = state.get("user_input", "").lower().strip()
            pending_schedule = self.get_context(state, "pending_schedule")

            # Check if we have a pending schedule awaiting confirmation
            if pending_schedule:
                return self._handle_pending_schedule(state, user_input, pending_schedule)

            # No pending schedule - generate new suggestions
            return self._generate_new_schedule(state)

        except Exception as e:
            return self.handle_error(state, e)

    def _generate_new_schedule(self, state: AgentState) -> AgentState:
        """Generate new schedule suggestions."""
        task_service = self.get_service("task_service")

        # Get incomplete tasks
        tasks = task_service.get_incomplete_tasks()

        if not tasks:
            response = "No tasks to schedule. Create some tasks first!"
            state = self.add_response(state, response)
            state["routing_decision"] = "END"
            return state

        # Generate schedule suggestions with time slots
        suggestions = self._generate_schedule_suggestions(tasks, state)

        # Store pending schedule in context for confirmation
        state = self.update_context(
            state,
            "pending_schedule",
            {
                "suggestions": suggestions,
                "created_at": datetime.now().isoformat(),
                "status": "awaiting_confirmation",
            },
        )

        # Format response with confirmation prompt
        response = self._format_response_with_confirmation(suggestions)

        # Update state - keep conversation going
        state = self.add_response(state, response)
        state["routing_decision"] = "END"  # Will continue via supervisor on next turn

        return state

    def _handle_pending_schedule(
        self, state: AgentState, user_input: str, pending_schedule: dict
    ) -> AgentState:
        """Handle user response to pending schedule."""
        suggestions = pending_schedule.get("suggestions", [])

        # Check for confirmation
        if self._is_confirmation(user_input):
            return self._confirm_and_create_schedule(state, suggestions)

        # Check for cancellation
        if self._is_cancellation(user_input):
            return self._cancel_schedule(state)

        # Check for modification request
        if self._is_modification(user_input):
            return self._handle_modification(state, user_input, suggestions)

        # Unclear response - ask for clarification
        response = (
            "I didn't quite understand. Would you like me to:\n\n"
            "- **Confirm** - Say 'yes' or 'schedule it' to create the time blocks\n"
            "- **Cancel** - Say 'no' or 'cancel' to discard this schedule\n"
            "- **Modify** - Say 'skip task 2' or 'change the order' to adjust\n\n"
            "What would you like to do?"
        )
        state = self.add_response(state, response)
        state["routing_decision"] = "END"
        return state

    def _is_confirmation(self, user_input: str) -> bool:
        """Check if user input indicates confirmation."""
        return any(kw in user_input for kw in self.CONFIRM_KEYWORDS)

    def _is_cancellation(self, user_input: str) -> bool:
        """Check if user input indicates cancellation."""
        return any(kw in user_input for kw in self.CANCEL_KEYWORDS)

    def _is_modification(self, user_input: str) -> bool:
        """Check if user input indicates modification request."""
        return any(kw in user_input for kw in self.MODIFY_KEYWORDS)

    def _confirm_and_create_schedule(
        self, state: AgentState, suggestions: list[dict]
    ) -> AgentState:
        """Create time blocks for confirmed schedule."""
        # Clear pending schedule FIRST to prevent duplicate creation on repeated confirmations
        state = self.update_context(state, "pending_schedule", None)

        calendar_service = self.get_service("calendar_service")
        created_blocks = []
        errors = []
        skipped = []

        # Calculate start time (next available hour)
        now = datetime.now()
        start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        for suggestion in suggestions:
            try:
                task_id = suggestion.get("task_id")
                duration = suggestion.get("duration", 60)
                end_time = start_time + timedelta(minutes=duration)

                # Check if a time block already exists for this task at this time
                if task_id:
                    existing_conflicts = calendar_service.find_conflicts(start_time, end_time)
                    already_scheduled = any(c.task_id == task_id for c in existing_conflicts)
                    if already_scheduled:
                        self.logger.info(
                            f"Skipping duplicate: {suggestion.get('task_title')} already scheduled"
                        )
                        skipped.append(suggestion.get("task_title", "Unknown"))
                        start_time = end_time + timedelta(minutes=10)
                        continue

                # Create time block
                block = calendar_service.create_time_block(
                    start_time=start_time,
                    end_time=end_time,
                    block_type=BlockType.TASK.value,
                    task_id=task_id,
                    is_flexible=True,
                    energy_level_required=suggestion.get("energy_level"),
                    notes=f"Scheduled: {suggestion.get('task_title')}",
                )
                created_blocks.append(
                    {
                        "task_title": suggestion.get("task_title"),
                        "start": start_time.strftime("%H:%M"),
                        "end": end_time.strftime("%H:%M"),
                        "block_id": block.id,
                    }
                )

                # Add 10-min buffer between tasks
                start_time = end_time + timedelta(minutes=10)

            except Exception as e:
                self.logger.error(f"Failed to create block for {suggestion.get('task_title')}: {e}")
                errors.append(suggestion.get("task_title", "Unknown"))

        # Format success response
        if created_blocks:
            response = "✅ **Schedule Created!**\n\n"
            for block in created_blocks:
                response += f"⏰ **{block['start']} - {block['end']}**: {block['task_title']}\n"

            if skipped:
                response += f"\nℹ️ Already scheduled (skipped): {', '.join(skipped)}"

            if errors:
                response += f"\n⚠️ Could not schedule: {', '.join(errors)}"

            response += "\n\nYour tasks are now scheduled. Good luck! 🎯"
        elif skipped:
            response = f"ℹ️ All tasks were already scheduled: {', '.join(skipped)}"
        else:
            response = "❌ Failed to create schedule. Please try again."

        state = self.add_response(state, response)
        state["routing_decision"] = "END"
        return state

    def _cancel_schedule(self, state: AgentState) -> AgentState:
        """Cancel pending schedule."""
        # Clear pending schedule
        state = self.update_context(state, "pending_schedule", None)

        response = (
            "No problem! I've cancelled the schedule. Let me know when you'd like to plan again."
        )
        state = self.add_response(state, response)
        state["routing_decision"] = "END"
        return state

    def _handle_modification(
        self, state: AgentState, user_input: str, suggestions: list[dict]
    ) -> AgentState:
        """Handle schedule modification requests."""
        # Parse which task to skip/modify
        import re

        skip_match = re.search(r"skip\s+(?:task\s+)?(\d+)", user_input)

        if skip_match:
            task_num = int(skip_match.group(1)) - 1  # Convert to 0-indexed
            if 0 <= task_num < len(suggestions):
                removed_task = suggestions.pop(task_num)

                if suggestions:
                    # Update pending schedule
                    state = self.update_context(
                        state,
                        "pending_schedule",
                        {
                            "suggestions": suggestions,
                            "created_at": datetime.now().isoformat(),
                            "status": "awaiting_confirmation",
                        },
                    )

                    response = f"✓ Removed **{removed_task['task_title']}** from the schedule.\n\n"
                    response += self._format_response_with_confirmation(suggestions)
                else:
                    # No tasks left
                    state = self.update_context(state, "pending_schedule", None)
                    response = "All tasks removed. The schedule has been cancelled."

                state = self.add_response(state, response)
                state["routing_decision"] = "END"
                return state

        # Couldn't parse modification - ask for clarification
        response = (
            "I can help you modify the schedule. You can:\n\n"
            "- Say **'skip task 1'** to remove a specific task\n"
            "- Say **'cancel'** to start over\n"
            "- Say **'confirm'** to proceed with current schedule\n\n"
            "What would you like to change?"
        )
        state = self.add_response(state, response)
        state["routing_decision"] = "END"
        return state

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
                "energy_level": str(task.estimated_energy_level),
                "position": i + 1,
                "reasoning": f"Priority: {task.priority}, Energy: {task.estimated_energy_level}",
            }
            suggestions.append(suggestion)

        return suggestions

    def _format_response_with_confirmation(self, suggestions: list[dict]) -> str:
        """Format schedule suggestions with confirmation prompt."""
        # Calculate estimated times
        now = datetime.now()
        start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        response = "📅 **Suggested Schedule:**\n\n"

        current_time = start_time
        for i, suggestion in enumerate(suggestions, 1):
            duration = suggestion.get("duration", 60)
            end_time = current_time + timedelta(minutes=duration)

            response += f"{i}. **{suggestion['task_title']}**\n"
            response += f"   ⏰ {current_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} ({duration} min)\n"
            response += f"   Priority: {suggestion['priority']} | Energy: {suggestion.get('energy_level', 'MEDIUM')}\n\n"

            # Add 10-min buffer
            current_time = end_time + timedelta(minutes=10)

        response += "---\n\n"
        response += "**Would you like me to create this schedule?**\n\n"
        response += "- Say **'yes'** or **'confirm'** to create time blocks\n"
        response += "- Say **'skip task 2'** to remove a task\n"
        response += "- Say **'no'** or **'cancel'** to discard\n"

        return response

    def _format_response(self, suggestions: list[dict]) -> str:
        """Format schedule suggestions response (legacy)."""
        return self._format_response_with_confirmation(suggestions)
