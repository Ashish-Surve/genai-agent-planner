"""Reusable prompt templates."""

from typing import Any


def format_prompt(template: str, **kwargs: Any) -> str:
    """
    Format a prompt template with variables.

    Args:
        template: Prompt template with {variable} placeholders
        **kwargs: Variable values

    Returns:
        Formatted prompt
    """
    return template.format(**kwargs)


# System prompts
PLANNING_SYSTEM_PROMPT = """You are a helpful AI assistant specializing in task planning
for people with ADHD. You understand the challenges of executive function, context switching,
and energy management. Always provide clear, actionable suggestions."""

SCHEDULING_SYSTEM_PROMPT = """You are an AI scheduling assistant that creates ADHD-friendly
schedules. Consider energy levels, break needs, buffer time, and context switching costs.
Prioritize realistic, sustainable schedules over cramming tasks."""

# Task extraction prompt
EXTRACT_TASKS_PROMPT = """Extract tasks from the following text. For each task, identify:
- Title (brief, clear)
- Estimated duration in minutes
- Energy level needed (LOW, MEDIUM, HIGH)
- Priority (URGENT, HIGH, MEDIUM, LOW)

Text: {text}

Return tasks in a structured format."""

# Time estimation prompt
ESTIMATE_DURATION_PROMPT = """Estimate how long this task will take, considering:
- Task complexity
- Need for focus
- Potential interruptions
- ADHD time-blindness (add buffer)

Task: {task_title}
Description: {task_description}

Provide estimate in minutes. Be realistic and generous."""
