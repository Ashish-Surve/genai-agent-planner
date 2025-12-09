# ADHD-13: Planning Agent

## Story Information
- **Epic**: Epic 3 - LangGraph Agents
- **Story ID**: ADHD-13
- **Estimated Time**: 3 hours
- **Status**: 📋 Not Started
- **Prerequisites**:
  - ✅ ADHD-12: Supervisor Agent
  - ✅ ADHD-11: LangGraph State & Base Agent
  - ✅ ADHD-8: Task Service
  - ✅ ADHD-9: Calendar Service
  - ✅ ADHD-10: Time Estimation Service

## Description

Implement the Planning Agent, which handles all task-related operations through natural language. The agent extracts task details from user input, estimates time and energy requirements, checks calendar availability, and creates or modifies tasks accordingly.

This is the first specialist agent and demonstrates the pattern that other agents will follow.

## Goals

1. Implement planning agent that extracts task details from natural language
2. Use LLM to parse user input into structured task data
3. Integrate with Task Service, Calendar Service, and Time Estimation Service
4. Provide intelligent scheduling suggestions
5. Handle task creation, updates, and queries
6. Create comprehensive prompts for task extraction

## Acceptance Criteria

### Planning Agent Implementation
- [ ] Inherits from BaseAgent
- [ ] Extracts task details from natural language
- [ ] Estimates time and energy using Time Estimation Service
- [ ] Checks calendar availability
- [ ] Creates tasks using Task Service
- [ ] Provides scheduling suggestions
- [ ] Handles errors gracefully

### Task Extraction
- [ ] Parses title, description, deadline from input
- [ ] Extracts priority level
- [ ] Identifies energy requirements
- [ ] Determines estimated duration
- [ ] Handles partial information
- [ ] Asks clarifying questions when needed

### Service Integration
- [ ] Uses Task Service for CRUD operations
- [ ] Uses Time Estimation Service for duration
- [ ] Uses Calendar Service for availability
- [ ] Updates state context with task data
- [ ] Returns user-friendly responses

### Testing
- [ ] Unit tests for task extraction
- [ ] Tests for service integration
- [ ] Tests for error handling
- [ ] Tests for various input formats
- [ ] Mock service dependencies

## Files to Create/Modify

### New Files
```
src/adhd_planner/agents/
└── planning_agent.py              # Planning agent implementation

src/adhd_planner/utils/prompts/
└── planning_prompts.py            # Planning agent prompts

tests/unit/
└── test_planning_agent.py        # Planning agent tests
```

## Implementation Steps

### Step 1: Create Planning Prompts (30 min)

Create `src/adhd_planner/utils/prompts/planning_prompts.py`:

```python
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


SCHEDULING_SUGGESTION_PROMPT = """Based on the task details and calendar availability, suggest when to schedule this task.

Task details:
- Title: {title}
- Duration: {duration} minutes
- Energy level: {energy_level}
- Deadline: {deadline}

Calendar availability:
{availability}

Energy patterns:
{energy_patterns}

Provide 2-3 scheduling suggestions with reasoning. Consider:
- Task energy requirements vs. user's energy patterns
- Available time slots
- Deadline proximity
- Buffer time for context switching

Format as JSON array:
[
  {
    "suggested_time": "2024-01-15T09:00:00",
    "reasoning": "Morning slot matches high energy requirement",
    "confidence": "high"
  }
]
"""
```

### Step 2: Create Planning Agent (90 min)

Create `src/adhd_planner/agents/planning_agent.py`:

```python
"""Planning Agent - Handles task creation and planning."""

import json
from datetime import datetime
from typing import Any

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from adhd_planner.models.task import TaskCreate
from adhd_planner.models.enums import Priority, EnergyLevel, TaskCategory
from adhd_planner.utils.prompts.planning_prompts import (
    PLANNING_SYSTEM_PROMPT,
    get_task_extraction_prompt,
    SCHEDULING_SUGGESTION_PROMPT,
)


class PlanningAgent(BaseAgent):
    """
    Planning Agent handles task creation and modification.

    Responsibilities:
    - Extract task details from natural language
    - Estimate time and energy requirements
    - Check calendar availability
    - Create tasks
    - Suggest scheduling times
    """

    def __init__(
        self,
        llm_service,
        task_service,
        calendar_service,
        time_estimation_service,
    ):
        """
        Initialize planning agent.

        Args:
            llm_service: LLM service for NLP
            task_service: Task service for CRUD operations
            calendar_service: Calendar service for availability
            time_estimation_service: Time estimation service
        """
        super().__init__(
            name="planning_agent",
            description="Creates and modifies tasks from natural language",
            llm_service=llm_service,
            task_service=task_service,
            calendar_service=calendar_service,
            time_estimation_service=time_estimation_service,
        )

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute planning logic.

        Args:
            state: Current agent state

        Returns:
            Updated state with task created and response
        """
        try:
            self.log_execution(state)

            user_input = state["user_input"]

            # Extract task details from natural language
            task_data = self._extract_task_details(user_input, state)

            # Check if clarification is needed
            if task_data.get("needs_clarification"):
                question = task_data.get("clarification_question")
                state = self.add_response(state, question)
                state["routing_decision"] = "END"
                return state

            # Refine time estimate using Time Estimation Service
            task_data = self._refine_time_estimate(task_data)

            # Create task using Task Service
            task = self._create_task(task_data)

            # Get scheduling suggestions
            suggestions = self._get_scheduling_suggestions(task, state)

            # Format response
            response = self._format_response(task, suggestions)

            # Update state
            state = self.add_response(state, response)
            state = self.update_context(state, "created_task", task.model_dump())
            state = self.update_context(state, "scheduling_suggestions", suggestions)
            state["routing_decision"] = "END"

            return state

        except Exception as e:
            return self.handle_error(state, e)

    def _extract_task_details(self, user_input: str, state: AgentState) -> dict[str, Any]:
        """
        Extract task details from natural language.

        Args:
            user_input: User's input
            state: Current state for context

        Returns:
            Extracted task details
        """
        llm_service = self.get_service("llm_service")

        # Build context
        context = {
            "current_time": datetime.now().isoformat(),
        }

        # Get extraction prompt
        prompt = get_task_extraction_prompt(user_input, context)

        # Call LLM
        response = llm_service.generate(
            prompt=prompt,
            system_prompt=PLANNING_SYSTEM_PROMPT,
            temperature=0.3,  # Low temperature for consistent extraction
        )

        # Parse JSON
        task_data = json.loads(response)

        self.logger.debug(f"Extracted task data: {task_data}")

        return task_data

    def _refine_time_estimate(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Refine time estimate using Time Estimation Service.

        Args:
            task_data: Extracted task data

        Returns:
            Task data with refined estimate
        """
        time_estimation_service = self.get_service("time_estimation_service")

        # Get initial estimate from extraction
        initial_estimate = task_data.get("estimated_duration_minutes")

        if initial_estimate:
            # Refine based on historical data
            refined_estimate = time_estimation_service.estimate_duration(
                title=task_data.get("title", ""),
                description=task_data.get("description", ""),
                category=task_data.get("category", "general"),
                initial_estimate=initial_estimate,
            )

            task_data["estimated_duration_minutes"] = refined_estimate
            self.logger.info(
                f"Refined time estimate: {initial_estimate} -> {refined_estimate} minutes"
            )

        return task_data

    def _create_task(self, task_data: dict[str, Any]) -> Any:
        """
        Create task using Task Service.

        Args:
            task_data: Task details

        Returns:
            Created task
        """
        task_service = self.get_service("task_service")

        # Convert to TaskCreate model
        task_create = TaskCreate(
            title=task_data["title"],
            description=task_data.get("description"),
            estimated_duration_minutes=task_data.get("estimated_duration_minutes"),
            priority=Priority[task_data.get("priority", "medium").upper()],
            energy_level=EnergyLevel[task_data.get("energy_level", "medium").upper()],
            category=TaskCategory[task_data.get("category", "general").upper()]
            if task_data.get("category")
            else None,
            deadline=datetime.fromisoformat(task_data["deadline"])
            if task_data.get("deadline")
            else None,
        )

        # Create task
        task = task_service.create_task(task_create)

        self.logger.info(f"Created task: {task.title} (ID: {task.id})")

        return task

    def _get_scheduling_suggestions(self, task: Any, state: AgentState) -> list[dict]:
        """
        Get scheduling suggestions for the task.

        Args:
            task: Created task
            state: Current state

        Returns:
            List of scheduling suggestions
        """
        calendar_service = self.get_service("calendar_service")
        llm_service = self.get_service("llm_service")

        # Get available time slots
        availability = calendar_service.find_available_slots(
            duration_minutes=task.estimated_duration_minutes or 60,
            days_ahead=7,
        )

        # Get energy patterns (from context if available)
        energy_patterns = self.get_context(state, "energy_patterns", {})

        # Build prompt
        prompt = SCHEDULING_SUGGESTION_PROMPT.format(
            title=task.title,
            duration=task.estimated_duration_minutes or 60,
            energy_level=task.energy_level.value,
            deadline=task.deadline.isoformat() if task.deadline else "None",
            availability=json.dumps(availability[:5]),  # Top 5 slots
            energy_patterns=json.dumps(energy_patterns) if energy_patterns else "Unknown",
        )

        # Get suggestions from LLM
        response = llm_service.generate(prompt=prompt, temperature=0.5)

        suggestions = json.loads(response)

        return suggestions

    def _format_response(self, task: Any, suggestions: list[dict]) -> str:
        """
        Format user-friendly response.

        Args:
            task: Created task
            suggestions: Scheduling suggestions

        Returns:
            Formatted response message
        """
        response = f"✅ Created task: **{task.title}**\n\n"

        if task.description:
            response += f"Description: {task.description}\n"

        response += f"Duration: {task.estimated_duration_minutes} minutes\n"
        response += f"Priority: {task.priority.value}\n"
        response += f"Energy: {task.energy_level.value}\n"

        if task.deadline:
            response += f"Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"

        if suggestions:
            response += "\n**Scheduling Suggestions:**\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                time_str = datetime.fromisoformat(
                    suggestion["suggested_time"]
                ).strftime("%a %b %d, %I:%M %p")
                response += f"{i}. {time_str} - {suggestion['reasoning']}\n"

        return response
```

### Step 3: Create Tests (60 min)

Create `tests/unit/test_planning_agent.py`:

```python
"""Tests for Planning Agent."""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from adhd_planner.agents.planning_agent import PlanningAgent
from adhd_planner.graph.state_utils import StateManager
from adhd_planner.models.enums import Priority, EnergyLevel, TaskStatus


class TestPlanningAgent:
    """Test planning agent functionality."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_service": Mock(),
            "task_service": Mock(),
            "calendar_service": Mock(),
            "time_estimation_service": Mock(),
        }

    @pytest.fixture
    def planning_agent(self, mock_services):
        """Create planning agent with mocks."""
        return PlanningAgent(**mock_services)

    def test_initialization(self, planning_agent):
        """Test agent initialization."""
        assert planning_agent.name == "planning_agent"
        assert planning_agent.description == "Creates and modifies tasks from natural language"

    def test_extract_and_create_task(self, planning_agent, mock_services):
        """Test full task creation flow."""
        # Mock LLM responses
        task_extraction = {
            "title": "Write report",
            "description": "Quarterly report",
            "estimated_duration_minutes": 120,
            "priority": "high",
            "energy_level": "high",
            "category": "work",
            "needs_clarification": False,
        }

        scheduling_suggestions = [
            {
                "suggested_time": "2024-01-15T09:00:00",
                "reasoning": "Morning high energy slot",
                "confidence": "high",
            }
        ]

        mock_services["llm_service"].generate.side_effect = [
            json.dumps(task_extraction),
            json.dumps(scheduling_suggestions),
        ]

        # Mock time estimation
        mock_services["time_estimation_service"].estimate_duration.return_value = 120

        # Mock task creation
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Write report"
        mock_task.description = "Quarterly report"
        mock_task.estimated_duration_minutes = 120
        mock_task.priority = Priority.HIGH
        mock_task.energy_level = EnergyLevel.HIGH
        mock_task.deadline = None
        mock_services["task_service"].create_task.return_value = mock_task

        # Mock calendar availability
        mock_services["calendar_service"].find_available_slots.return_value = [
            {"start": "2024-01-15T09:00:00", "end": "2024-01-15T11:00:00"}
        ]

        # Execute
        state = StateManager.create_initial_state("Add task: write report, 2 hours")
        result = planning_agent.execute(state)

        # Verify task was created
        assert mock_services["task_service"].create_task.called
        assert result["routing_decision"] == "END"
        assert len(result["messages"]) == 2  # User + AI response
        assert "Write report" in result["messages"][1].content

    def test_needs_clarification(self, planning_agent, mock_services):
        """Test when agent needs clarification."""
        task_extraction = {
            "title": "",
            "needs_clarification": True,
            "clarification_question": "What task would you like to create?",
        }

        mock_services["llm_service"].generate.return_value = json.dumps(task_extraction)

        state = StateManager.create_initial_state("Add a task")
        result = planning_agent.execute(state)

        # Should not create task, should ask question
        assert not mock_services["task_service"].create_task.called
        assert "What task would you like to create?" in result["messages"][1].content

    def test_time_estimate_refinement(self, planning_agent, mock_services):
        """Test time estimate refinement."""
        task_extraction = {
            "title": "Write code",
            "estimated_duration_minutes": 60,
            "priority": "medium",
            "energy_level": "medium",
            "category": "work",
            "needs_clarification": False,
        }

        mock_services["llm_service"].generate.side_effect = [
            json.dumps(task_extraction),
            json.dumps([]),  # No scheduling suggestions
        ]

        # Time estimation service refines to 90 minutes
        mock_services["time_estimation_service"].estimate_duration.return_value = 90

        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Write code"
        mock_task.estimated_duration_minutes = 90  # Refined estimate
        mock_task.priority = Priority.MEDIUM
        mock_task.energy_level = EnergyLevel.MEDIUM
        mock_task.deadline = None
        mock_services["task_service"].create_task.return_value = mock_task

        mock_services["calendar_service"].find_available_slots.return_value = []

        state = StateManager.create_initial_state("Add task: write code, 1 hour")
        result = planning_agent.execute(state)

        # Verify refinement was called
        assert mock_services["time_estimation_service"].estimate_duration.called
        call_args = mock_services["time_estimation_service"].estimate_duration.call_args
        assert call_args.kwargs["initial_estimate"] == 60

    def test_error_handling(self, planning_agent, mock_services):
        """Test error handling."""
        # Make LLM raise exception
        mock_services["llm_service"].generate.side_effect = Exception("LLM error")

        state = StateManager.create_initial_state("Add task")
        result = planning_agent.execute(state)

        # Should have error in state
        assert result["error"] is not None
        assert "planning_agent" in result["error"]

    def test_scheduling_suggestions(self, planning_agent, mock_services):
        """Test that scheduling suggestions are provided."""
        task_extraction = {
            "title": "Important meeting prep",
            "estimated_duration_minutes": 60,
            "priority": "high",
            "energy_level": "high",
            "category": "work",
            "deadline": "2024-01-20T14:00:00",
            "needs_clarification": False,
        }

        suggestions = [
            {
                "suggested_time": "2024-01-19T09:00:00",
                "reasoning": "Day before deadline, morning high energy",
                "confidence": "high",
            },
            {
                "suggested_time": "2024-01-19T14:00:00",
                "reasoning": "Alternative afternoon slot",
                "confidence": "medium",
            },
        ]

        mock_services["llm_service"].generate.side_effect = [
            json.dumps(task_extraction),
            json.dumps(suggestions),
        ]

        mock_services["time_estimation_service"].estimate_duration.return_value = 60

        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Important meeting prep"
        mock_task.estimated_duration_minutes = 60
        mock_task.priority = Priority.HIGH
        mock_task.energy_level = EnergyLevel.HIGH
        mock_task.deadline = datetime(2024, 1, 20, 14, 0)
        mock_services["task_service"].create_task.return_value = mock_task

        mock_services["calendar_service"].find_available_slots.return_value = [
            {"start": "2024-01-19T09:00:00", "end": "2024-01-19T10:00:00"}
        ]

        state = StateManager.create_initial_state(
            "Add task: prep for meeting, due tomorrow at 2pm"
        )
        result = planning_agent.execute(state)

        # Should include suggestions in response
        response = result["messages"][1].content
        assert "Scheduling Suggestions" in response
        assert "Jan 19" in response  # Date from suggestion
```

### Step 4: Update Package Initialization (10 min)

Update `src/adhd_planner/agents/__init__.py`:

```python
"""AI agents for the ADHD Planner system."""

from adhd_planner.agents.base import BaseAgent
from adhd_planner.agents.supervisor import SupervisorAgent
from adhd_planner.agents.planning_agent import PlanningAgent

__all__ = ["BaseAgent", "SupervisorAgent", "PlanningAgent"]
```

Update `src/adhd_planner/utils/prompts/__init__.py`:

```python
"""Prompt templates for LLM interactions."""

from adhd_planner.utils.prompts.supervisor_prompts import (
    SUPERVISOR_SYSTEM_PROMPT,
    get_routing_prompt,
    DIRECT_RESPONSE_PROMPT,
)
from adhd_planner.utils.prompts.planning_prompts import (
    PLANNING_SYSTEM_PROMPT,
    get_task_extraction_prompt,
    SCHEDULING_SUGGESTION_PROMPT,
)

__all__ = [
    "SUPERVISOR_SYSTEM_PROMPT",
    "get_routing_prompt",
    "DIRECT_RESPONSE_PROMPT",
    "PLANNING_SYSTEM_PROMPT",
    "get_task_extraction_prompt",
    "SCHEDULING_SUGGESTION_PROMPT",
]
```

## Testing Checklist

- [ ] Run `uv run pytest tests/unit/test_planning_agent.py -v`
- [ ] All planning agent tests pass
- [ ] Task extraction works for various inputs
- [ ] Time estimation refinement works
- [ ] Task creation via service works
- [ ] Scheduling suggestions are generated
- [ ] Clarification questions work
- [ ] Error handling is robust
- [ ] Response formatting is user-friendly

## Success Criteria

### Functionality
- [ ] Extracts task details from natural language
- [ ] Creates tasks using Task Service
- [ ] Refines time estimates
- [ ] Provides scheduling suggestions
- [ ] Handles missing information gracefully
- [ ] All tests pass

### Code Quality
- [ ] Type hints on all methods
- [ ] Comprehensive docstrings
- [ ] Clean service integration
- [ ] Proper error handling
- [ ] Follows agent pattern

### Testing
- [ ] Full workflow tested
- [ ] Service mocks work correctly
- [ ] Edge cases covered
- [ ] Error scenarios tested

## Implementation Notes

### Natural Language Processing

The agent uses LLM for NLP because:
- Handles varied user input styles
- Infers missing information intelligently
- Adapts to context
- More flexible than regex patterns

### Service Coordination

The agent coordinates multiple services:
1. **LLM Service**: Extract task details
2. **Time Estimation Service**: Refine duration
3. **Task Service**: Create task
4. **Calendar Service**: Find available slots
5. **LLM Service** (again): Generate scheduling suggestions

### Response Formatting

User-friendly responses include:
- Confirmation of task creation
- Task details summary
- Scheduling suggestions with reasoning
- Clear, ADHD-friendly formatting

## Next Story

After completing this story, proceed to:
- **ADHD-14**: Scheduling Agent - Generate optimized schedules

## Questions or Issues?

Review the test output and service integration if issues arise.

Good luck! 🚀
