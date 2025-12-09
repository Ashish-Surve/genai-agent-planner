# ADHD-15: Suggestion Agent

## Story Information
- **Epic**: Epic 3 - LangGraph Agents
- **Story ID**: ADHD-15
- **Estimated Time**: 2 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-14: Scheduling Agent
  - ✅ ADHD-8: Task Service
  - ✅ ADHD-9: Calendar Service

## Description

Implement the Suggestion Agent, which provides proactive task recommendations based on current context. The agent analyzes available time, current energy level, task characteristics, and priorities to suggest what the user should work on right now.

This agent helps ADHD users overcome decision paralysis by providing clear, contextual recommendations.

## Goals

1. Analyze current context (time, energy, available tasks)
2. Rank tasks by suitability for the current moment
3. Provide 3-5 task suggestions with clear reasoning
4. Consider multiple factors (priority, deadline, energy match, duration)
5. Explain why each task is suggested
6. Handle "what should I do now?" queries

## Acceptance Criteria

### Suggestion Agent Implementation
- [ ] Inherits from BaseAgent
- [ ] Analyzes current context effectively
- [ ] Ranks tasks by suitability
- [ ] Provides 3-5 suggestions
- [ ] Clear reasoning for each suggestion
- [ ] Handles no available tasks gracefully
- [ ] Error handling

### Context Analysis
- [ ] Determines current time of day
- [ ] Infers or uses provided energy level
- [ ] Checks calendar for available time
- [ ] Considers task deadlines
- [ ] Evaluates task characteristics
- [ ] Weighs multiple factors

### Recommendation Logic
- [ ] Tasks with urgent deadlines ranked higher
- [ ] Energy level matching (high-energy tasks in morning)
- [ ] Duration matching (short tasks if little time)
- [ ] Priority consideration
- [ ] Recent work patterns (if available)

### Response Format
- [ ] Top 3-5 task suggestions
- [ ] Clear reasoning for each
- [ ] Estimated time for each
- [ ] Urgency indicators
- [ ] User-friendly formatting

### Testing
- [ ] Unit tests for context analysis
- [ ] Tests for ranking logic
- [ ] Tests with various scenarios
- [ ] Edge case handling
- [ ] Mock service dependencies

## Files to Create/Modify

### New Files
```
src/adhd_planner/agents/
└── suggestion_agent.py           # Suggestion agent implementation

src/adhd_planner/utils/prompts/
└── suggestion_prompts.py         # Suggestion prompts

tests/unit/
└── test_suggestion_agent.py     # Suggestion agent tests
```

## Implementation Steps

### Step 1: Create Suggestion Prompts (20 min)

Create `src/adhd_planner/utils/prompts/suggestion_prompts.py`:

```python
"""Prompts for the Suggestion Agent."""

SUGGESTION_SYSTEM_PROMPT = """You are the Suggestion Agent for ADHD Planner.

Your role is to recommend what the user should work on RIGHT NOW based on:
1. Current time and day
2. User's current energy level
3. Available time
4. Task characteristics (priority, deadline, energy, duration)
5. Context switching costs

Provide 3-5 task suggestions ranked by suitability. For each suggestion, explain WHY it's a good choice right now.

Consider:
- **Urgency**: Tasks with approaching deadlines
- **Energy Match**: High-energy tasks when user has high energy
- **Time Available**: Short tasks if limited time
- **Priority**: Higher priority tasks first
- **Context**: Similar to what user was recently working on
- **Quick Wins**: Easy tasks to build momentum

Respond in JSON format with ranked suggestions.
"""


def get_suggestion_prompt(
    tasks: list[dict],
    current_context: dict,
) -> str:
    """
    Create prompt for task suggestions.

    Args:
        tasks: Available tasks
        current_context: Current context (time, energy, calendar)

    Returns:
        Formatted prompt
    """
    prompt = f"""Suggest what the user should work on right now.

**Current Context:**
- Time: {current_context.get('current_time', 'unknown')}
- Day: {current_context.get('day_of_week', 'unknown')}
- Energy Level: {current_context.get('energy_level', 'medium')}
- Available Time: {current_context.get('available_time_minutes', 'unknown')} minutes
- Time of Day: {current_context.get('time_of_day', 'unknown')} (morning/afternoon/evening)

**Available Tasks:**
"""

    for i, task in enumerate(tasks[:20], 1):  # Limit to 20 tasks
        prompt += f"\n{i}. **{task.get('title')}**"
        prompt += f"\n   - Duration: {task.get('estimated_duration_minutes', '?')} min"
        prompt += f"\n   - Priority: {task.get('priority', 'medium')}"
        prompt += f"\n   - Energy: {task.get('energy_level', 'medium')}"
        if task.get('deadline'):
            prompt += f"\n   - Deadline: {task['deadline']}"
        if task.get('category'):
            prompt += f"\n   - Category: {task['category']}"
        prompt += f"\n   - Task ID: {task.get('id')}"

    prompt += """

Rank the top 3-5 tasks by suitability for RIGHT NOW. Respond in JSON:
{
  "suggestions": [
    {
      "task_id": 1,
      "task_title": "Task name",
      "rank": 1,
      "suitability_score": 95,
      "reasoning": "Why this task is perfect right now",
      "estimated_duration": 60,
      "urgency_level": "high|medium|low"
    }
  ]
}

Prioritize tasks that match current energy and available time.
"""

    return prompt
```

### Step 2: Create Suggestion Agent (45 min)

Create `src/adhd_planner/agents/suggestion_agent.py`:

```python
"""Suggestion Agent - Recommends tasks based on context."""

import json
from datetime import datetime
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from adhd_planner.utils.prompts.suggestion_prompts import (
    SUGGESTION_SYSTEM_PROMPT,
    get_suggestion_prompt,
)


class SuggestionAgent(BaseAgent):
    """
    Suggestion Agent recommends tasks based on current context.

    Responsibilities:
    - Analyze current context (time, energy, availability)
    - Rank tasks by suitability
    - Provide 3-5 recommendations with reasoning
    - Help users overcome decision paralysis
    """

    def __init__(self, llm_service, task_service, calendar_service):
        """
        Initialize suggestion agent.

        Args:
            llm_service: LLM service
            task_service: Task service
            calendar_service: Calendar service
        """
        super().__init__(
            name="suggestion_agent",
            description="Recommends tasks based on current context",
            llm_service=llm_service,
            task_service=task_service,
            calendar_service=calendar_service,
        )

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute suggestion logic.

        Args:
            state: Current agent state

        Returns:
            Updated state with task suggestions
        """
        try:
            self.log_execution(state)

            # Get available tasks
            tasks = self._get_available_tasks()

            if not tasks:
                response = "You don't have any incomplete tasks! Time to relax or add new tasks. 🎉"
                state = self.add_response(state, response)
                state["routing_decision"] = "END"
                return state

            # Build current context
            current_context = self._build_current_context(state)

            # Get suggestions from LLM
            suggestions = self._get_suggestions(tasks, current_context)

            # Format response
            response = self._format_suggestions(suggestions, current_context)

            # Update state
            state = self.add_response(state, response)
            state = self.update_context(state, "task_suggestions", suggestions)
            state["routing_decision"] = "END"

            return state

        except Exception as e:
            return self.handle_error(state, e)

    def _get_available_tasks(self) -> list[dict]:
        """
        Get tasks that could be worked on now.

        Returns:
            List of task dictionaries
        """
        task_service = self.get_service("task_service")

        tasks = task_service.get_incomplete_tasks()

        # Convert to dicts
        task_dicts = []
        for task in tasks:
            task_dicts.append({
                "id": task.id,
                "title": task.title,
                "estimated_duration_minutes": task.estimated_duration_minutes,
                "priority": task.priority.value,
                "energy_level": task.energy_level.value,
                "category": task.category.value if task.category else None,
                "deadline": task.deadline.isoformat() if task.deadline else None,
            })

        self.logger.info(f"Found {len(task_dicts)} available tasks")

        return task_dicts

    def _build_current_context(self, state: AgentState) -> dict:
        """
        Build current context for suggestions.

        Args:
            state: Current state

        Returns:
            Context dictionary
        """
        now = datetime.now()

        # Determine time of day
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

        # Get energy level from state or infer from time of day
        energy_level = self.get_context(state, "current_energy_level")
        if not energy_level:
            # Infer from time of day
            energy_map = {
                "morning": "high",
                "afternoon": "medium",
                "evening": "low",
            }
            energy_level = energy_map[time_of_day]

        # Check calendar for available time
        calendar_service = self.get_service("calendar_service")
        next_event = calendar_service.get_next_event()

        if next_event:
            time_until_next = (next_event.start_time - now).total_seconds() / 60
            available_time = max(int(time_until_next) - 15, 15)  # Subtract buffer
        else:
            available_time = 120  # Assume 2 hours if no next event

        context = {
            "current_time": now.isoformat(),
            "day_of_week": now.strftime("%A"),
            "time_of_day": time_of_day,
            "energy_level": energy_level,
            "available_time_minutes": available_time,
        }

        self.logger.debug(f"Current context: {context}")

        return context

    def _get_suggestions(
        self, tasks: list[dict], current_context: dict
    ) -> list[dict]:
        """
        Get task suggestions from LLM.

        Args:
            tasks: Available tasks
            current_context: Current context

        Returns:
            List of suggestions
        """
        llm_service = self.get_service("llm_service")

        # Build prompt
        prompt = get_suggestion_prompt(tasks, current_context)

        # Get suggestions
        response = llm_service.generate(
            prompt=prompt,
            system_prompt=SUGGESTION_SYSTEM_PROMPT,
            temperature=0.4,  # Moderate temperature for some variety
        )

        # Parse JSON
        result = json.loads(response)
        suggestions = result.get("suggestions", [])

        self.logger.info(f"Generated {len(suggestions)} suggestions")

        return suggestions

    def _format_suggestions(
        self, suggestions: list[dict], context: dict
    ) -> str:
        """
        Format suggestions for user.

        Args:
            suggestions: Task suggestions
            context: Current context

        Returns:
            Formatted response
        """
        energy = context.get("energy_level", "medium")
        time_of_day = context.get("time_of_day", "today")
        available_time = context.get("available_time_minutes", "unknown")

        response = f"💡 **Task Suggestions for {time_of_day}**\n"
        response += f"Your energy: {energy.upper()} | Available time: ~{available_time} min\n\n"

        if not suggestions:
            response += "I couldn't find suitable tasks for right now. Try adjusting task priorities or adding new tasks."
            return response

        response += "Here's what I recommend:\n\n"

        for i, suggestion in enumerate(suggestions[:5], 1):
            urgency_emoji = {
                "high": "🔥",
                "medium": "⚡",
                "low": "📌",
            }.get(suggestion.get("urgency_level", "medium"), "📌")

            response += f"{i}. {urgency_emoji} **{suggestion['task_title']}**\n"
            response += f"   ⏱️ ~{suggestion.get('estimated_duration', '?')} min\n"
            response += f"   💭 {suggestion['reasoning']}\n\n"

        response += "Ready to start? Just say 'start task 1' or pick any task above!"

        return response
```

### Step 3: Create Tests (30 min)

Create `tests/unit/test_suggestion_agent.py`:

```python
"""Tests for Suggestion Agent."""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from adhd_planner.agents.suggestion_agent import SuggestionAgent
from adhd_planner.graph.state_utils import StateManager


class TestSuggestionAgent:
    """Test suggestion agent."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_service": Mock(),
            "task_service": Mock(),
            "calendar_service": Mock(),
        }

    @pytest.fixture
    def suggestion_agent(self, mock_services):
        """Create suggestion agent."""
        return SuggestionAgent(**mock_services)

    @pytest.fixture
    def mock_tasks(self):
        """Create mock tasks."""
        tasks = []
        for i in range(5):
            task = MagicMock()
            task.id = i + 1
            task.title = f"Task {i+1}"
            task.estimated_duration_minutes = 30 + (i * 15)
            task.priority = MagicMock(value=["high", "medium", "low"][i % 3])
            task.energy_level = MagicMock(value=["high", "medium", "low"][i % 3])
            task.category = MagicMock(value="work")
            task.deadline = None
            tasks.append(task)
        return tasks

    def test_initialization(self, suggestion_agent):
        """Test agent initialization."""
        assert suggestion_agent.name == "suggestion_agent"

    def test_get_suggestions(self, suggestion_agent, mock_services, mock_tasks):
        """Test getting task suggestions."""
        # Mock task service
        mock_services["task_service"].get_incomplete_tasks.return_value = mock_tasks

        # Mock calendar service
        mock_services["calendar_service"].get_next_event.return_value = None

        # Mock LLM suggestions
        suggestions_response = {
            "suggestions": [
                {
                    "task_id": 1,
                    "task_title": "Task 1",
                    "rank": 1,
                    "suitability_score": 95,
                    "reasoning": "High priority and matches your current high energy",
                    "estimated_duration": 30,
                    "urgency_level": "high",
                },
                {
                    "task_id": 2,
                    "task_title": "Task 2",
                    "rank": 2,
                    "suitability_score": 85,
                    "reasoning": "Good fit for available time",
                    "estimated_duration": 45,
                    "urgency_level": "medium",
                },
            ]
        }

        mock_services["llm_service"].generate.return_value = json.dumps(
            suggestions_response
        )

        # Execute
        state = StateManager.create_initial_state("What should I work on?")
        result = suggestion_agent.execute(state)

        # Verify
        assert result["routing_decision"] == "END"
        response = result["messages"][1].content
        assert "Task Suggestions" in response
        assert "Task 1" in response
        assert "Task 2" in response
        assert "High priority and matches your current high energy" in response

    def test_no_tasks_available(self, suggestion_agent, mock_services):
        """Test when no tasks are available."""
        mock_services["task_service"].get_incomplete_tasks.return_value = []

        state = StateManager.create_initial_state("What should I do?")
        result = suggestion_agent.execute(state)

        response = result["messages"][1].content
        assert "don't have any incomplete tasks" in response.lower()

    def test_context_building(self, suggestion_agent, mock_services, mock_tasks):
        """Test current context building."""
        mock_services["task_service"].get_incomplete_tasks.return_value = mock_tasks

        # Mock next event in 90 minutes
        next_event = MagicMock()
        from datetime import timedelta
        next_event.start_time = datetime.now() + timedelta(minutes=90)
        mock_services["calendar_service"].get_next_event.return_value = next_event

        suggestions_response = {"suggestions": []}
        mock_services["llm_service"].generate.return_value = json.dumps(
            suggestions_response
        )

        state = StateManager.create_initial_state("What should I work on?")
        result = suggestion_agent.execute(state)

        # Verify LLM was called with context
        call_args = mock_services["llm_service"].generate.call_args
        prompt = call_args.kwargs["prompt"]
        assert "Available Time:" in prompt
        # Should have ~75 min (90 - 15 buffer)

    def test_energy_level_from_state(self, suggestion_agent, mock_services, mock_tasks):
        """Test using energy level from state."""
        mock_services["task_service"].get_incomplete_tasks.return_value = mock_tasks
        mock_services["calendar_service"].get_next_event.return_value = None

        suggestions_response = {"suggestions": []}
        mock_services["llm_service"].generate.return_value = json.dumps(
            suggestions_response
        )

        # Set energy level in state
        state = StateManager.create_initial_state("What should I work on?")
        state = StateManager.update_context(state, "current_energy_level", "low")

        result = suggestion_agent.execute(state)

        # Verify energy level was used
        call_args = mock_services["llm_service"].generate.call_args
        prompt = call_args.kwargs["prompt"]
        assert "Energy Level: low" in prompt

    def test_error_handling(self, suggestion_agent, mock_services):
        """Test error handling."""
        mock_services["task_service"].get_incomplete_tasks.side_effect = Exception(
            "Database error"
        )

        state = StateManager.create_initial_state("What should I do?")
        result = suggestion_agent.execute(state)

        assert result["error"] is not None
        assert "suggestion_agent" in result["error"]
```

### Step 4: Update Package Files (5 min)

Update `src/adhd_planner/agents/__init__.py`:

```python
"""AI agents for the ADHD Planner system."""

from adhd_planner.agents.base import BaseAgent
from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.agents.scheduling_agent import SchedulingAgent
from adhd_planner.agents.suggestion_agent import SuggestionAgent

__all__ = [
    "BaseAgent",
    "SupervisorAgent",
    "PlanningAgent",
    "SchedulingAgent",
    "SuggestionAgent",
]
```

## Testing Checklist

- [ ] Run `uv run pytest tests/unit/test_suggestion_agent.py -v`
- [ ] All tests pass
- [ ] Suggestions generated correctly
- [ ] Context analysis works
- [ ] Energy level handling works
- [ ] Available time calculation works
- [ ] No tasks scenario handled
- [ ] Error handling works

## Success Criteria

### Functionality
- [ ] Provides 3-5 task suggestions
- [ ] Clear reasoning for each
- [ ] Context-aware recommendations
- [ ] Energy level matching
- [ ] Time-aware suggestions
- [ ] All tests pass

### Code Quality
- [ ] Type hints
- [ ] Docstrings
- [ ] Clean service integration
- [ ] Error handling
- [ ] Logging

### Testing
- [ ] Suggestion logic tested
- [ ] Context building tested
- [ ] Edge cases covered
- [ ] Mock services work

## Implementation Notes

### Context-Aware Recommendations

The agent considers:
- **Time of Day**: Morning/afternoon/evening affects energy
- **Available Time**: Suggests tasks that fit
- **Energy Level**: Matches task energy requirements
- **Urgency**: Approaching deadlines prioritized
- **Quick Wins**: Sometimes suggests easy tasks for momentum

### Decision Paralysis

ADHD users often struggle with "what to do next." This agent:
- Provides clear, ranked options
- Explains reasoning
- Reduces cognitive load
- Builds confidence through structure

## Next Story

After completing this story, proceed to:
- **ADHD-16**: Graph Builder & Integration

Good luck! 🚀
