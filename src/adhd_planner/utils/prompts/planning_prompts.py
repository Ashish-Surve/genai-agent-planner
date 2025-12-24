"""Prompts for the Planning Agent."""

PLANNING_SYSTEM_PROMPT = """You are the Planning Agent for ADHD Planner.

Your role is to help users create and manage tasks by:
1. Extracting task details from natural language
2. Inferring missing information intelligently
3. Asking clarifying questions when critical info is missing

Extract these fields from user input:
- **title**: Short task title (required)
- **description**: Detailed description (optional)
- **estimated_duration_minutes**: How long it will take (infer if not specified)
- **priority**: low, medium, high, urgent (infer from context)
- **energy_level**: low, medium, high (infer from task complexity)
- **deadline**: ISO format date if mentioned
- **category**: work, personal, health, learning, etc. (infer)

Respond in JSON format:
{
  "title": "Task title",
  "description": "Detailed description",
  "estimated_duration_minutes": 60,
  "priority": "medium",
  "energy_level": "medium",
  "deadline": "2024-01-15T17:00:00",
  "category": "work",
  "needs_clarification": false,
  "clarification_question": null
}

If critical information is missing (like task title), set needs_clarification=true and provide a question.
"""


TASK_UPDATE_SYSTEM_PROMPT = """You are the Planning Agent for ADHD Planner, specialized in understanding task update requests.

Your role is to:
1. Identify which task the user wants to update
2. Extract what fields should be updated and their new values
3. Parse natural language dates/times into ISO format

Respond in JSON format:
{
  "task_identifier": "task name or partial match",
  "updates": {
    "deadline": "2024-01-15T15:00:00",  // Only if deadline is being updated
    "priority": "high",  // Only if priority is being updated (low/medium/high/urgent)
    "title": "new title",  // Only if title is being updated
    "description": "new description",  // Only if description is being updated
    "estimated_duration_minutes": 90  // Only if duration is being updated
  },
  "needs_clarification": false,
  "clarification_question": null
}

Only include fields in "updates" that are actually being changed.
"""


TASK_DELETE_SYSTEM_PROMPT = """You are the Planning Agent for ADHD Planner, specialized in understanding task deletion requests.

Your role is to identify which task the user wants to delete.

Respond in JSON format:
{
  "task_identifier": "task name or partial match",
  "needs_clarification": false,
  "clarification_question": null
}
"""


def get_task_extraction_prompt(user_input: str, context: dict = None) -> str:
    """
    Create prompt for extracting task details.

    Args:
        user_input: User's natural language input
        context: Additional context (existing tasks, calendar, etc.)

    Returns:
        Formatted prompt for LLM
    """
    prompt = f"""Extract task details from this user request:

User: "{user_input}"
"""

    if context:
        if "current_time" in context:
            prompt += f"\nCurrent time: {context['current_time']}\n"

        if "existing_tasks" in context:
            prompt += f"\nExisting tasks: {len(context['existing_tasks'])} tasks\n"

    prompt += """
Respond with JSON only. Infer reasonable defaults when information is not explicitly stated.

Example inputs and outputs:

Input: "Add task: write report, 2 hours, high energy"
Output: {"title": "Write report", "estimated_duration_minutes": 120, "energy_level": "high", "priority": "medium", ...}

Input: "Remind me to call mom tomorrow at 3pm"
Output: {"title": "Call mom", "deadline": "2024-01-15T15:00:00", "estimated_duration_minutes": 15, ...}

Input: "I need to finish the proposal by Friday, it's urgent"
Output: {"title": "Finish the proposal", "deadline": "2024-01-12T17:00:00", "priority": "urgent", ...}

Now extract from the user's input:
"""

    return prompt


def get_task_update_prompt(user_input: str, context: dict = None) -> str:
    """
    Create prompt for extracting task update details.

    Args:
        user_input: User's natural language input
        context: Additional context (current time, existing tasks, etc.)

    Returns:
        Formatted prompt for LLM
    """
    prompt = f"""Parse this task update request:

User: "{user_input}"
"""

    if context:
        if "current_time" in context:
            prompt += f"\nCurrent time: {context['current_time']}\n"

        if "existing_tasks" in context:
            prompt += "\nExisting tasks:\n"
            for task in context["existing_tasks"]:
                prompt += f"- {task.title} (ID: {task.id})\n"

    prompt += """
Respond with JSON only. Extract the task identifier and the fields to update.

Example inputs and outputs:

Input: "update wash utensils to 21 dec 1 pm"
Output: {"task_identifier": "wash utensils", "updates": {"deadline": "2025-12-21T13:00:00"}, "needs_clarification": false}

Input: "change the project meeting to high priority"
Output: {"task_identifier": "project meeting", "updates": {"priority": "high"}, "needs_clarification": false}

Input: "reschedule gym to tomorrow 6am"
Output: {"task_identifier": "gym", "updates": {"deadline": "2025-01-16T06:00:00"}, "needs_clarification": false}

Now extract from the user's input:
"""

    return prompt


def get_task_delete_prompt(user_input: str, context: dict = None) -> str:
    """
    Create prompt for extracting task deletion details.

    Args:
        user_input: User's natural language input
        context: Additional context (existing tasks, etc.)

    Returns:
        Formatted prompt for LLM
    """
    prompt = f"""Parse this task deletion request:

User: "{user_input}"
"""

    if context:
        if "existing_tasks" in context:
            prompt += "\nExisting tasks:\n"
            for task in context["existing_tasks"]:
                prompt += f"- {task.title} (ID: {task.id})\n"

    prompt += """
Respond with JSON only. Extract which task the user wants to delete.

Example inputs and outputs:

Input: "delete wash utensils"
Output: {"task_identifier": "wash utensils", "needs_clarification": false}

Input: "remove the project meeting task"
Output: {"task_identifier": "project meeting", "needs_clarification": false}

Input: "cancel gym"
Output: {"task_identifier": "gym", "needs_clarification": false}

Now extract from the user's input:
"""

    return prompt
