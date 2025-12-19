"""Prompt templates for LLM interactions."""

from adhd_planner.utils.prompts.supervisor_prompts import (
    DIRECT_RESPONSE_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT,
    get_routing_prompt,
)

__all__ = [
    "SUPERVISOR_SYSTEM_PROMPT",
    "get_routing_prompt",
    "DIRECT_RESPONSE_PROMPT",
]
