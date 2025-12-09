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
