"""Scheduling Agent - Interactive single-task scheduling with natural language."""

import re
from datetime import datetime, timedelta
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from adhd_planner.models.enums import BlockType


class SchedulingAgent(BaseAgent):
    """
    Scheduling Agent for interactive single-task scheduling.

    Responsibilities:
    - Find tasks by natural language description
    - Suggest optimal time slots for scheduling
    - Negotiate time interactively with user
    - Create time blocks upon confirmation
    """

    # Keywords indicating user confirmation
    CONFIRM_KEYWORDS = [
        "yes",
        "confirm",
        "do it",
        "ok",
        "sure",
        "go ahead",
        "sounds good",
        "let's do it",
        "perfect",
        "great",
        "that works",
    ]
    CANCEL_KEYWORDS = ["no", "cancel", "nevermind", "never mind", "stop", "don't", "forget it"]

    # Time-related keywords for negotiation
    TIME_ADJUSTMENT_PATTERNS = [
        r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",  # "2pm", "2:30pm", "14:00"
        r"(morning|afternoon|evening|night)",
        r"(tomorrow|today|next\s+\w+)",
        r"(earlier|later|before|after)",
        r"(\d+)\s*(hour|minute|min|hr)s?\s*(earlier|later|before|after)?",
    ]

    def __init__(self, llm_service, task_service, calendar_service):
        """Initialize scheduling agent."""
        super().__init__(
            name="scheduling_agent",
            description="Interactive single-task scheduling with time negotiation",
            llm_service=llm_service,
            task_service=task_service,
            calendar_service=calendar_service,
        )

    def execute(self, state: AgentState) -> AgentState:
        """Execute interactive single-task scheduling."""
        try:
            self.log_execution(state)

            user_input = state.get("user_input", "").lower().strip()
            pending_task = self.get_context(state, "pending_task_schedule")

            # Check if we have a pending task schedule awaiting response
            if pending_task:
                return self._handle_pending_task(state, user_input, pending_task)

            # No pending task - try to find a task from user input
            return self._find_and_suggest_task(state, user_input)

        except Exception as e:
            return self.handle_error(state, e)

    def _find_and_suggest_task(self, state: AgentState, user_input: str) -> AgentState:
        """Find a task from user's natural language description and suggest a time."""
        task_service = self.get_service("task_service")

        # Get all incomplete tasks
        tasks = task_service.get_incomplete_tasks()

        if not tasks:
            response = "You don't have any tasks to schedule. Create some tasks first!"
            state = self.add_response(state, response)
            state["routing_decision"] = "END"
            return state

        # Try to find a matching task from user input
        matched_task = self._find_task_by_description(tasks, user_input)

        if not matched_task:
            # No match found - show available tasks and ask user to clarify
            response = self._format_task_selection_prompt(tasks)
            state = self.add_response(state, response)
            state["routing_decision"] = "END"
            return state

        # Found a task - suggest a time slot
        suggested_time = self._suggest_time_slot(state, matched_task)

        # Store pending task for confirmation/negotiation
        state = self.update_context(
            state,
            "pending_task_schedule",
            {
                "task_id": matched_task.id,
                "task_title": matched_task.title,
                "duration": matched_task.estimated_duration_minutes or 60,
                "energy_level": str(matched_task.estimated_energy_level),
                "priority": str(matched_task.priority),
                "suggested_start": suggested_time.isoformat(),
                "status": "awaiting_confirmation",
            },
        )

        # Format the suggestion
        response = self._format_time_suggestion(matched_task, suggested_time)

        state = self.add_response(state, response)
        state["routing_decision"] = "END"
        return state

    def _find_task_by_description(self, tasks: list[Any], user_input: str) -> Any | None:
        """Find a task that matches the user's natural language description."""
        user_input_lower = user_input.lower()

        # Remove common scheduling phrases to isolate task description
        scheduling_phrases = [
            "schedule",
            "plan",
            "block",
            "time for",
            "work on",
            "do",
            "the",
            "my",
            "a",
            "an",
            "task",
            "please",
            "can you",
            "i want to",
            "i need to",
            "let's",
            "help me",
        ]
        search_terms = user_input_lower
        for phrase in scheduling_phrases:
            search_terms = search_terms.replace(phrase, " ")
        search_terms = " ".join(search_terms.split()).strip()

        if not search_terms:
            return None

        # Score each task based on how well it matches
        best_match = None
        best_score = 0

        for task in tasks:
            score = self._calculate_match_score(task, search_terms)
            if score > best_score:
                best_score = score
                best_match = task

        # Only return if we have a reasonable match (at least 1 word matches)
        if best_score >= 1:
            return best_match

        return None

    def _calculate_match_score(self, task: Any, search_terms: str) -> float:
        """Calculate how well a task matches the search terms."""
        score = 0.0
        task_title_lower = task.title.lower()
        task_desc_lower = (task.description or "").lower()

        search_words = search_terms.split()

        for word in search_words:
            if len(word) < 2:
                continue
            # Exact word match in title (highest value)
            if word in task_title_lower.split():
                score += 3
            # Partial match in title
            elif word in task_title_lower:
                score += 2
            # Match in description
            elif word in task_desc_lower:
                score += 1

        return score

    def _suggest_time_slot(self, _state: AgentState, task: Any) -> datetime:
        """Suggest an optimal time slot for the task."""
        calendar_service = self.get_service("calendar_service")

        now = datetime.now()
        duration = task.estimated_duration_minutes or 60

        # Start looking from the next hour
        candidate_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        # Try to find a free slot in the next 8 hours
        for _ in range(16):  # Check 16 half-hour slots
            candidate_end = candidate_start + timedelta(minutes=duration)

            # Check for conflicts
            conflicts = calendar_service.find_conflicts(candidate_start, candidate_end)
            if not conflicts:
                return candidate_start

            # Move to next slot (30-minute increments)
            candidate_start += timedelta(minutes=30)

        # If no free slot found in next 8 hours, just use next hour
        return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    def _format_task_selection_prompt(self, tasks: list[Any]) -> str:
        """Format a prompt asking user to specify which task to schedule."""
        response = "I couldn't find a matching task. Here are your current tasks:\n\n"

        # Show up to 8 tasks sorted by priority
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                -{"URGENT": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(str(t.priority).upper(), 1),
                t.deadline or datetime.now() + timedelta(days=365),
            ),
        )

        for i, task in enumerate(sorted_tasks[:8], 1):
            priority_emoji = {"URGENT": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(
                str(task.priority).upper(), "⚪"
            )
            response += f"{i}. {priority_emoji} **{task.title}**"
            if task.estimated_duration_minutes:
                response += f" ({task.estimated_duration_minutes} min)"
            response += "\n"

        response += "\n**Which task would you like to schedule?**\n"
        response += "Just describe it (e.g., 'schedule the report' or 'plan time for emails')"

        return response

    def _format_time_suggestion(self, task: Any, suggested_time: datetime) -> str:
        """Format the time suggestion for user confirmation."""
        duration = task.estimated_duration_minutes or 60
        end_time = suggested_time + timedelta(minutes=duration)

        response = f"📋 **Task:** {task.title}\n\n"

        response += f"⏰ **Suggested time:** {suggested_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"

        # Add "today" or day name for clarity
        if suggested_time.date() == datetime.now().date():
            response += " (today)"
        elif suggested_time.date() == (datetime.now() + timedelta(days=1)).date():
            response += " (tomorrow)"
        else:
            response += f" ({suggested_time.strftime('%A')})"

        response += f"\n⏱️ **Duration:** {duration} minutes\n"

        if task.priority:
            priority_emoji = {"URGENT": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(
                str(task.priority).upper(), "⚪"
            )
            response += f"📊 **Priority:** {priority_emoji} {task.priority}\n"

        response += "\n---\n"
        response += "**Does this time work for you?**\n\n"
        response += "- Say **'yes'** to schedule it\n"
        response += (
            "- Suggest a different time (e.g., '3pm', 'tomorrow morning', '2 hours later')\n"
        )
        response += "- Say **'cancel'** to skip\n"

        return response

    def _handle_pending_task(
        self, state: AgentState, user_input: str, pending_task: dict
    ) -> AgentState:
        """Handle user response to a pending task schedule."""
        # Check for confirmation
        if self._is_confirmation(user_input):
            return self._confirm_and_create_block(state, pending_task)

        # Check for cancellation
        if self._is_cancellation(user_input):
            return self._cancel_scheduling(state)

        # Try to parse a time adjustment
        new_time = self._parse_time_adjustment(user_input, pending_task)
        if new_time:
            return self._update_suggested_time(state, pending_task, new_time)

        # Unclear response - ask for clarification
        response = (
            "I didn't quite catch that. You can:\n\n"
            "- Say **'yes'** to confirm the suggested time\n"
            "- Tell me a different time (e.g., '2pm', 'tomorrow at 10', '1 hour later')\n"
            "- Say **'cancel'** to skip scheduling this task\n"
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

    def _parse_time_adjustment(self, user_input: str, pending_task: dict) -> datetime | None:
        """Parse user's time adjustment request."""
        current_time = datetime.fromisoformat(pending_task["suggested_start"])
        now = datetime.now()

        user_input_lower = user_input.lower().strip()

        # Handle relative adjustments: "1 hour later", "30 minutes earlier"
        relative_match = re.search(
            r"(\d+)\s*(hour|hr|minute|min)s?\s*(later|earlier|before|after)?", user_input_lower
        )
        if relative_match:
            amount = int(relative_match.group(1))
            unit = relative_match.group(2)
            direction = relative_match.group(3) or "later"

            if unit in ("hour", "hr"):
                delta = timedelta(hours=amount)
            else:
                delta = timedelta(minutes=amount)

            if direction in ("earlier", "before"):
                return current_time - delta
            else:
                return current_time + delta

        # Handle "tomorrow" variations
        if "tomorrow" in user_input_lower:
            tomorrow = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            # Check if a specific time is also mentioned
            time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", user_input_lower)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                period = time_match.group(3)
                if period == "pm" and hour < 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                tomorrow = tomorrow.replace(hour=hour, minute=minute)
            return tomorrow

        # Handle time of day: "morning", "afternoon", "evening"
        if "morning" in user_input_lower:
            base_date = now.date() if now.hour < 12 else (now + timedelta(days=1)).date()
            return datetime.combine(base_date, datetime.min.time().replace(hour=9))
        if "afternoon" in user_input_lower:
            base_date = now.date() if now.hour < 17 else (now + timedelta(days=1)).date()
            return datetime.combine(base_date, datetime.min.time().replace(hour=14))
        if "evening" in user_input_lower:
            base_date = now.date() if now.hour < 20 else (now + timedelta(days=1)).date()
            return datetime.combine(base_date, datetime.min.time().replace(hour=18))

        # Handle specific times: "2pm", "14:30", "2:30pm"
        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", user_input_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            period = time_match.group(3)

            # Handle 12-hour format
            if period == "pm" and hour < 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
            # If no am/pm and hour is small, assume PM for work hours
            elif not period and 1 <= hour <= 6:
                hour += 12

            new_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # If the time has passed today, schedule for tomorrow
            if new_time <= now:
                new_time += timedelta(days=1)

            return new_time

        return None

    def _update_suggested_time(
        self, state: AgentState, pending_task: dict, new_time: datetime
    ) -> AgentState:
        """Update the suggested time and show new proposal."""
        # Update pending task with new time
        pending_task["suggested_start"] = new_time.isoformat()
        state = self.update_context(state, "pending_task_schedule", pending_task)

        duration = pending_task["duration"]
        end_time = new_time + timedelta(minutes=duration)

        response = f"📋 **Task:** {pending_task['task_title']}\n\n"
        response += f"⏰ **Updated time:** {new_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"

        if new_time.date() == datetime.now().date():
            response += " (today)"
        elif new_time.date() == (datetime.now() + timedelta(days=1)).date():
            response += " (tomorrow)"
        else:
            response += f" ({new_time.strftime('%A')})"

        response += f"\n⏱️ **Duration:** {duration} minutes\n"
        response += "\n**Does this work?** (yes/no or suggest another time)"

        state = self.add_response(state, response)
        state["routing_decision"] = "END"
        return state

    def _confirm_and_create_block(self, state: AgentState, pending_task: dict) -> AgentState:
        """Create the time block for the confirmed task."""
        # Clear pending task FIRST to prevent duplicates
        state = self.update_context(state, "pending_task_schedule", None)

        calendar_service = self.get_service("calendar_service")

        task_id = pending_task["task_id"]
        task_title = pending_task["task_title"]
        duration = pending_task["duration"]
        start_time = datetime.fromisoformat(pending_task["suggested_start"])
        end_time = start_time + timedelta(minutes=duration)

        try:
            # Check for existing block for this task
            existing_conflicts = calendar_service.find_conflicts(start_time, end_time)
            already_scheduled = any(c.task_id == task_id for c in existing_conflicts)

            if already_scheduled:
                response = f"ℹ️ **{task_title}** is already scheduled at this time."
                state = self.add_response(state, response)
                state["routing_decision"] = "END"
                return state

            # Create time block
            calendar_service.create_time_block(
                start_time=start_time,
                end_time=end_time,
                block_type=BlockType.TASK.value,
                task_id=task_id,
                is_flexible=True,
                energy_level_required=pending_task.get("energy_level"),
                notes=f"Scheduled: {task_title}",
            )

            response = "✅ **Scheduled!**\n\n"
            response += f"📋 **{task_title}**\n"
            response += f"⏰ {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"

            if start_time.date() == datetime.now().date():
                response += " today"
            elif start_time.date() == (datetime.now() + timedelta(days=1)).date():
                response += " tomorrow"

            response += "\n\nWant to schedule another task? Just tell me which one!"

        except Exception as e:
            self.logger.error(f"Failed to create block for {task_title}: {e}")
            response = f"❌ Sorry, I couldn't create the time block. Error: {str(e)}"

        state = self.add_response(state, response)
        state["routing_decision"] = "END"
        return state

    def _cancel_scheduling(self, state: AgentState) -> AgentState:
        """Cancel the pending task scheduling."""
        state = self.update_context(state, "pending_task_schedule", None)

        response = "No problem! Let me know when you want to schedule a task."
        state = self.add_response(state, response)
        state["routing_decision"] = "END"
        return state
