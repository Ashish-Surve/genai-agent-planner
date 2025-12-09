# ADHD-14: Scheduling Agent

## Story Information
- **Epic**: Epic 3 - LangGraph Agents
- **Story ID**: ADHD-14
- **Estimated Time**: 4 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-13: Planning Agent
  - ✅ ADHD-9: Calendar Service
  - ✅ ADHD-8: Task Service

## Description

Implement the Scheduling Agent, which generates ADHD-friendly daily and weekly schedules. The agent considers task priorities, energy levels, deadlines, available time, and ADHD-specific factors like buffer time and context switching penalties.

This is the most complex agent, as it must balance multiple constraints and optimize schedules for ADHD users.

## Goals

1. Generate daily and weekly schedules from incomplete tasks
2. Apply ADHD-friendly scheduling rules (buffer time, energy matching)
3. Provide multiple schedule options for user choice
4. Handle scheduling constraints (deadlines, energy patterns, conflicts)
5. Create time blocks in calendar
6. Explain scheduling decisions with clear reasoning

## Acceptance Criteria

### Scheduling Agent Implementation
- [ ] Inherits from BaseAgent
- [ ] Generates daily schedules on request
- [ ] Generates weekly schedules on request
- [ ] Applies ADHD-friendly rules automatically
- [ ] Provides 2-3 schedule options
- [ ] Creates time blocks when user selects option
- [ ] Clear explanations of scheduling decisions

### ADHD-Friendly Rules
- [ ] Adds buffer time between tasks (10-15 minutes)
- [ ] Matches task energy to time of day
- [ ] Groups similar tasks to reduce context switching
- [ ] Avoids overloading any single day
- [ ] Schedules breaks appropriately
- [ ] Respects user energy patterns

### Schedule Generation
- [ ] Fetches incomplete tasks
- [ ] Gets calendar availability
- [ ] Considers deadlines and priorities
- [ ] Uses LLM for intelligent scheduling
- [ ] Returns multiple options
- [ ] Formats schedules user-friendly

### Time Block Creation
- [ ] Creates time blocks for selected schedule
- [ ] Links time blocks to tasks
- [ ] Updates task scheduling status
- [ ] Handles creation errors gracefully

### Testing
- [ ] Unit tests for schedule generation
- [ ] Tests for ADHD rules application
- [ ] Tests for time block creation
- [ ] Tests with various constraint scenarios
- [ ] Mock service dependencies

## Files to Create/Modify

### New Files
```
src/adhd_planner/agents/
└── scheduling_agent.py           # Scheduling agent implementation

src/adhd_planner/utils/prompts/
└── scheduling_prompts.py         # Scheduling prompts

tests/unit/
└── test_scheduling_agent.py     # Scheduling agent tests
```

## Implementation Steps

### Step 1: Create Scheduling Prompts (45 min)

Create `src/adhd_planner/utils/prompts/scheduling_prompts.py`:

```python
"""Prompts for the Scheduling Agent."""

SCHEDULING_SYSTEM_PROMPT = """You are the Scheduling Agent for ADHD Planner.

Your role is to create ADHD-friendly schedules that:
1. Match task energy requirements to user's energy patterns
2. Add buffer time between tasks (10-15 minutes)
3. Group similar tasks to reduce context switching
4. Respect deadlines and priorities
5. Avoid overwhelming the user
6. Include breaks for sustainability

ADHD-Friendly Scheduling Rules:
- **Buffer Time**: Always add 10-15 min between tasks for transitions
- **Energy Matching**: Schedule high-energy tasks during peak energy times
- **Context Switching**: Minimize switches between different task types
- **Urgency First**: Prioritize tasks with approaching deadlines
- **Breaks**: Include 5-10 min breaks every 90-120 minutes
- **Realistic Load**: Don't overschedule; leave room for flexibility

Provide 2-3 schedule options with different approaches (e.g., deadline-focused vs. energy-optimized).
"""


def get_schedule_generation_prompt(
    tasks: list[dict],
    available_slots: list[dict],
    energy_patterns: dict,
    day_or_week: str,
) -> str:
    """
    Create prompt for schedule generation.

    Args:
        tasks: List of incomplete tasks
        available_slots: Available time slots
        energy_patterns: User's energy patterns
        day_or_week: "day" or "week"

    Returns:
        Formatted prompt
    """
    prompt = f"""Generate {day_or_week} schedule options for the following tasks.

**Tasks to Schedule:**
"""

    for i, task in enumerate(tasks[:15], 1):  # Limit to 15 tasks
        prompt += f"\n{i}. **{task.get('title')}**"
        prompt += f"\n   - Duration: {task.get('estimated_duration_minutes', '?')} min"
        prompt += f"\n   - Priority: {task.get('priority', 'medium')}"
        prompt += f"\n   - Energy: {task.get('energy_level', 'medium')}"
        if task.get('deadline'):
            prompt += f"\n   - Deadline: {task['deadline']}"
        if task.get('category'):
            prompt += f"\n   - Category: {task['category']}"

    prompt += f"\n\n**Available Time Slots:**\n"
    for slot in available_slots[:10]:  # Top 10 slots
        prompt += f"- {slot['start']} to {slot['end']}\n"

    prompt += f"\n**Energy Patterns:**\n"
    if energy_patterns:
        prompt += f"{energy_patterns}\n"
    else:
        prompt += "Unknown - use general patterns (morning: high, afternoon: medium, evening: low)\n"

    prompt += f"""
Create 2-3 different {day_or_week} schedule options. Each option should:
1. Apply all ADHD-friendly rules
2. Fit tasks into available slots
3. Have a clear theme (e.g., "Deadline-Focused", "Energy-Optimized", "Balanced")

Respond in JSON format:
{{
  "options": [
    {{
      "name": "Deadline-Focused Schedule",
      "description": "Prioritizes urgent tasks first",
      "schedule": [
        {{
          "start_time": "2024-01-15T09:00:00",
          "end_time": "2024-01-15T10:30:00",
          "task_id": 1,
          "task_title": "Complete urgent report",
          "includes_buffer": true,
          "reasoning": "High priority with approaching deadline"
        }}
      ],
      "total_tasks_scheduled": 5,
      "estimated_completion_rate": "85%"
    }}
  ]
}}
"""

    return prompt
```

### Step 2: Create Scheduling Agent (120 min)

Create `src/adhd_planner/agents/scheduling_agent.py`:

```python
"""Scheduling Agent - Generates ADHD-friendly schedules."""

import json
from datetime import datetime, timedelta
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from adhd_planner.models.time_block import TimeBlockCreate
from adhd_planner.utils.prompts.scheduling_prompts import (
    SCHEDULING_SYSTEM_PROMPT,
    get_schedule_generation_prompt,
)


class SchedulingAgent(BaseAgent):
    """
    Scheduling Agent generates optimized schedules.

    Responsibilities:
    - Generate daily/weekly schedules
    - Apply ADHD-friendly scheduling rules
    - Provide multiple schedule options
    - Create time blocks for selected schedule
    - Explain scheduling decisions
    """

    def __init__(self, llm_service, task_service, calendar_service):
        """
        Initialize scheduling agent.

        Args:
            llm_service: LLM service
            task_service: Task service
            calendar_service: Calendar service
        """
        super().__init__(
            name="scheduling_agent",
            description="Generates ADHD-friendly schedules",
            llm_service=llm_service,
            task_service=task_service,
            calendar_service=calendar_service,
        )

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute scheduling logic.

        Args:
            state: Current agent state

        Returns:
            Updated state with schedule options
        """
        try:
            self.log_execution(state)

            user_input = state["user_input"].lower()

            # Determine if day or week schedule
            day_or_week = "week" if "week" in user_input else "day"

            # Get incomplete tasks
            tasks = self._get_tasks_to_schedule()

            if not tasks:
                response = "You don't have any incomplete tasks to schedule! 🎉"
                state = self.add_response(state, response)
                state["routing_decision"] = "END"
                return state

            # Get available time slots
            days_ahead = 7 if day_or_week == "week" else 1
            available_slots = self._get_available_slots(days_ahead)

            # Get energy patterns
            energy_patterns = self.get_context(state, "energy_patterns", {})

            # Generate schedule options
            schedule_options = self._generate_schedule_options(
                tasks, available_slots, energy_patterns, day_or_week
            )

            # Format response
            response = self._format_schedule_options(schedule_options, day_or_week)

            # Update state
            state = self.add_response(state, response)
            state = self.update_context(state, "schedule_options", schedule_options)
            state["routing_decision"] = "END"

            return state

        except Exception as e:
            return self.handle_error(state, e)

    def _get_tasks_to_schedule(self) -> list[dict]:
        """
        Get incomplete tasks that need scheduling.

        Returns:
            List of task dictionaries
        """
        task_service = self.get_service("task_service")

        tasks = task_service.get_incomplete_tasks()

        # Convert to dicts for LLM
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

        self.logger.info(f"Found {len(task_dicts)} tasks to schedule")

        return task_dicts

    def _get_available_slots(self, days_ahead: int) -> list[dict]:
        """
        Get available time slots.

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of available time slots
        """
        calendar_service = self.get_service("calendar_service")

        # Get slots for the next N days
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)

        slots = calendar_service.get_available_slots(
            start_date=start_date,
            end_date=end_date,
            min_duration_minutes=30,
        )

        self.logger.info(f"Found {len(slots)} available slots")

        return slots

    def _generate_schedule_options(
        self,
        tasks: list[dict],
        available_slots: list[dict],
        energy_patterns: dict,
        day_or_week: str,
    ) -> list[dict]:
        """
        Generate schedule options using LLM.

        Args:
            tasks: Tasks to schedule
            available_slots: Available time slots
            energy_patterns: User's energy patterns
            day_or_week: "day" or "week"

        Returns:
            List of schedule options
        """
        llm_service = self.get_service("llm_service")

        # Build prompt
        prompt = get_schedule_generation_prompt(
            tasks, available_slots, energy_patterns, day_or_week
        )

        # Generate schedules
        response = llm_service.generate(
            prompt=prompt,
            system_prompt=SCHEDULING_SYSTEM_PROMPT,
            temperature=0.7,  # Higher temperature for creative scheduling
        )

        # Parse JSON
        result = json.loads(response)
        options = result.get("options", [])

        self.logger.info(f"Generated {len(options)} schedule options")

        return options

    def _format_schedule_options(
        self, options: list[dict], day_or_week: str
    ) -> str:
        """
        Format schedule options for user.

        Args:
            options: Schedule options
            day_or_week: "day" or "week"

        Returns:
            Formatted response
        """
        response = f"📅 Here are {len(options)} {day_or_week} schedule options:\n\n"

        for i, option in enumerate(options, 1):
            response += f"**Option {i}: {option['name']}**\n"
            response += f"{option['description']}\n"
            response += f"Tasks scheduled: {option.get('total_tasks_scheduled', '?')}\n"
            response += f"Estimated completion: {option.get('estimated_completion_rate', '?')}\n\n"

            # Show first few scheduled items as preview
            schedule = option.get('schedule', [])
            for j, item in enumerate(schedule[:3], 1):
                start = datetime.fromisoformat(item['start_time'])
                end = datetime.fromisoformat(item['end_time'])
                response += f"  {j}. {start.strftime('%a %I:%M %p')} - {end.strftime('%I:%M %p')}: {item['task_title']}\n"

            if len(schedule) > 3:
                response += f"  ... and {len(schedule) - 3} more tasks\n"

            response += "\n"

        response += "To create time blocks for an option, say: 'Use option 1' or 'Schedule option 2'"

        return response

    def create_time_blocks_from_schedule(
        self, schedule: list[dict]
    ) -> list[Any]:
        """
        Create time blocks from a schedule.

        Args:
            schedule: Schedule items

        Returns:
            Created time blocks
        """
        calendar_service = self.get_service("calendar_service")
        task_service = self.get_service("task_service")

        created_blocks = []

        for item in schedule:
            # Create time block
            time_block_create = TimeBlockCreate(
                start_time=datetime.fromisoformat(item['start_time']),
                end_time=datetime.fromisoformat(item['end_time']),
                task_id=item.get('task_id'),
                title=item.get('task_title', 'Scheduled task'),
                description=item.get('reasoning'),
            )

            block = calendar_service.create_time_block(time_block_create)
            created_blocks.append(block)

            # Update task as scheduled
            if item.get('task_id'):
                task_service.mark_task_scheduled(item['task_id'], block.id)

        self.logger.info(f"Created {len(created_blocks)} time blocks")

        return created_blocks
```

### Step 3: Create Tests (60 min)

Create `tests/unit/test_scheduling_agent.py`:

```python
"""Tests for Scheduling Agent."""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from adhd_planner.agents.scheduling_agent import SchedulingAgent
from adhd_planner.graph.state_utils import StateManager


class TestSchedulingAgent:
    """Test scheduling agent."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_service": Mock(),
            "task_service": Mock(),
            "calendar_service": Mock(),
        }

    @pytest.fixture
    def scheduling_agent(self, mock_services):
        """Create scheduling agent."""
        return SchedulingAgent(**mock_services)

    @pytest.fixture
    def mock_tasks(self):
        """Create mock tasks."""
        tasks = []
        for i in range(3):
            task = MagicMock()
            task.id = i + 1
            task.title = f"Task {i+1}"
            task.estimated_duration_minutes = 60
            task.priority = MagicMock(value="medium")
            task.energy_level = MagicMock(value="medium")
            task.category = MagicMock(value="work")
            task.deadline = None
            tasks.append(task)
        return tasks

    def test_initialization(self, scheduling_agent):
        """Test agent initialization."""
        assert scheduling_agent.name == "scheduling_agent"

    def test_generate_day_schedule(self, scheduling_agent, mock_services, mock_tasks):
        """Test generating daily schedule."""
        # Mock task service
        mock_services["task_service"].get_incomplete_tasks.return_value = mock_tasks

        # Mock calendar service
        mock_services["calendar_service"].get_available_slots.return_value = [
            {"start": "2024-01-15T09:00:00", "end": "2024-01-15T12:00:00"}
        ]

        # Mock LLM schedule generation
        schedule_response = {
            "options": [
                {
                    "name": "Balanced Schedule",
                    "description": "Evenly distributed tasks",
                    "schedule": [
                        {
                            "start_time": "2024-01-15T09:00:00",
                            "end_time": "2024-01-15T10:00:00",
                            "task_id": 1,
                            "task_title": "Task 1",
                            "includes_buffer": True,
                            "reasoning": "Morning high energy",
                        }
                    ],
                    "total_tasks_scheduled": 3,
                    "estimated_completion_rate": "90%",
                }
            ]
        }

        mock_services["llm_service"].generate.return_value = json.dumps(schedule_response)

        # Execute
        state = StateManager.create_initial_state("Plan my day")
        result = scheduling_agent.execute(state)

        # Verify
        assert result["routing_decision"] == "END"
        assert len(result["messages"]) == 2
        response = result["messages"][1].content
        assert "schedule options" in response.lower()
        assert "Balanced Schedule" in response

    def test_no_tasks_to_schedule(self, scheduling_agent, mock_services):
        """Test when there are no tasks."""
        mock_services["task_service"].get_incomplete_tasks.return_value = []

        state = StateManager.create_initial_state("Plan my day")
        result = scheduling_agent.execute(state)

        # Should inform user no tasks
        response = result["messages"][1].content
        assert "don't have any incomplete tasks" in response.lower()

    def test_weekly_schedule(self, scheduling_agent, mock_services, mock_tasks):
        """Test generating weekly schedule."""
        mock_services["task_service"].get_incomplete_tasks.return_value = mock_tasks
        mock_services["calendar_service"].get_available_slots.return_value = []

        schedule_response = {
            "options": [
                {
                    "name": "Week Plan",
                    "description": "Spread across the week",
                    "schedule": [],
                    "total_tasks_scheduled": 10,
                    "estimated_completion_rate": "80%",
                }
            ]
        }

        mock_services["llm_service"].generate.return_value = json.dumps(schedule_response)

        state = StateManager.create_initial_state("Plan my week")
        result = scheduling_agent.execute(state)

        # Verify week schedule was requested
        llm_call_args = mock_services["llm_service"].generate.call_args
        prompt = llm_call_args.kwargs["prompt"]
        assert "week" in prompt.lower()

    def test_create_time_blocks(self, scheduling_agent, mock_services):
        """Test creating time blocks from schedule."""
        schedule = [
            {
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "task_id": 1,
                "task_title": "Task 1",
                "reasoning": "Morning slot",
            }
        ]

        mock_block = MagicMock()
        mock_block.id = 100
        mock_services["calendar_service"].create_time_block.return_value = mock_block

        blocks = scheduling_agent.create_time_blocks_from_schedule(schedule)

        # Verify blocks were created
        assert len(blocks) == 1
        assert mock_services["calendar_service"].create_time_block.called
        assert mock_services["task_service"].mark_task_scheduled.called

    def test_error_handling(self, scheduling_agent, mock_services):
        """Test error handling."""
        mock_services["task_service"].get_incomplete_tasks.side_effect = Exception(
            "Database error"
        )

        state = StateManager.create_initial_state("Plan my day")
        result = scheduling_agent.execute(state)

        assert result["error"] is not None
        assert "scheduling_agent" in result["error"]
```

### Step 4: Update Package Files (10 min)

Update `src/adhd_planner/agents/__init__.py`:

```python
"""AI agents for the ADHD Planner system."""

from adhd_planner.agents.base import BaseAgent
from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.agents.scheduling_agent import SchedulingAgent

__all__ = ["BaseAgent", "SupervisorAgent", "PlanningAgent", "SchedulingAgent"]
```

## Testing Checklist

- [ ] Run `uv run pytest tests/unit/test_scheduling_agent.py -v`
- [ ] All tests pass
- [ ] Day schedule generation works
- [ ] Week schedule generation works
- [ ] Multiple schedule options provided
- [ ] Time block creation works
- [ ] ADHD rules are applied
- [ ] Error handling works
- [ ] No tasks scenario handled

## Success Criteria

### Functionality
- [ ] Generates day and week schedules
- [ ] Provides 2-3 options
- [ ] Applies ADHD-friendly rules
- [ ] Creates time blocks
- [ ] Clear explanations
- [ ] All tests pass

### Code Quality
- [ ] Type hints
- [ ] Docstrings
- [ ] Clean service integration
- [ ] Error handling
- [ ] Logging

### Testing
- [ ] Schedule generation tested
- [ ] Time block creation tested
- [ ] Edge cases covered
- [ ] Mock services work

## Implementation Notes

### ADHD-Friendly Scheduling

Key principles:
1. **Buffer Time**: 10-15 min between tasks
2. **Energy Matching**: High-energy tasks in morning
3. **Context Switching**: Group similar tasks
4. **Realistic Load**: Don't overschedule
5. **Breaks**: Regular breaks for sustainability

### Multiple Options

Providing options empowers ADHD users:
- Different scheduling philosophies
- User chooses what feels right
- Reduces decision paralysis through structure

## Next Story

After completing this story, proceed to:
- **ADHD-15**: Suggestion Agent

Good luck! 🚀
