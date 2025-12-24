"""Planning Agent - Handles all task operations via unified query interface."""

import json
from datetime import datetime

from adhd_planner.agents.base import BaseAgent
from adhd_planner.graph.state import AgentState
from adhd_planner.services.query_models import MethodCall, QueryResult
from adhd_planner.services.query_validator import MethodCallValidator
from adhd_planner.utils.prompts.unified_query_prompts import (
    UNIFIED_QUERY_SYSTEM_PROMPT,
    get_unified_query_prompt,
)


class PlanningAgent(BaseAgent):
    """
    Planning Agent with unified natural language query interface.

    Handles all task operations (CRUD + advanced queries) through a single
    unified interface that translates natural language to TaskService method calls.

    Features:
    - Natural language query translation via LLM
    - Support for sorting, pagination, aggregation
    - Comprehensive validation and error handling
    - Task identifier resolution for updates/deletes
    """

    def __init__(self, llm_service, task_service):
        """Initialize planning agent."""
        super().__init__(
            name="planning_agent",
            description="Handles all task operations via unified query interface",
            llm_service=llm_service,
            task_service=task_service,
        )
        self.validator = MethodCallValidator()

    def execute(self, state: AgentState) -> AgentState:
        """Execute planning logic with unified query interface."""
        try:
            self.log_execution(state)
            return self._execute_unified_query(state)
        except Exception as e:
            self.logger.error(f"Planning agent execution failed: {e}", exc_info=True)
            return self.handle_error(state, e)

    # ========================================================================
    # UNIFIED QUERY INTERFACE
    # ========================================================================

    def _execute_unified_query(self, state: AgentState) -> AgentState:
        """
        Execute unified query workflow for all operations.

        Workflow:
        1. Build context (current time, existing tasks if needed)
        2. LLM: Translate NL → MethodCall
        3. Check for clarification needs
        4. Validate method call
        5. Resolve task identifiers (for update/delete/start/complete)
        6. Execute via TaskService.query()
        7. Format response
        8. Update state

        Args:
            state: Current agent state

        Returns:
            Updated agent state with response
        """
        user_input = state["user_input"]
        self.logger.info(f"Processing query: '{user_input}'")

        # 1. Build context for LLM
        context = self._build_query_context(user_input)

        # 2. Translate NL → MethodCall using LLM
        method_call = self._translate_nl_to_method_call(user_input, context)

        # 3. Check for clarification
        if method_call.needs_clarification:
            self.logger.info(f"Clarification needed: {method_call.clarification_question}")
            state = self.add_response(state, method_call.clarification_question)
            state["routing_decision"] = "END"
            return state

        # 4. Validate method call
        is_valid, error = self.validator.validate(method_call)
        if not is_valid:
            self.logger.warning(f"Validation failed: {error}")
            response = f"❌ I couldn't process that request: {error}"
            state = self.add_response(state, response)
            state["routing_decision"] = "END"
            return state

        # 5. Resolve task identifiers (if needed)
        if self._needs_task_resolution(method_call):
            method_call = self._resolve_task_identifiers(method_call, context)
            if method_call.needs_clarification:
                self.logger.info(
                    f"Clarification after resolution: {method_call.clarification_question}"
                )
                state = self.add_response(state, method_call.clarification_question)
                state["routing_decision"] = "END"
                return state

        # 5.5. Convert parameter types (e.g., ISO datetime strings to datetime objects)
        method_call = self._convert_parameter_types(method_call)

        # 6. Execute query via TaskService
        task_service = self.get_service("task_service")
        query_result = task_service.query(user_input, method_call)

        # 7. Format response
        response = self._format_query_result(query_result)

        # 8. Update state
        state = self.add_response(state, response)
        state["routing_decision"] = "END"

        return state

    # ========================================================================
    # LLM TRANSLATION
    # ========================================================================

    def _translate_nl_to_method_call(self, user_input: str, context: dict) -> MethodCall:
        """
        Translate natural language to MethodCall using LLM.

        Args:
            user_input: User's natural language query
            context: Context dict with current_time, existing_tasks, etc.

        Returns:
            MethodCall structure from LLM

        Note:
            If LLM fails to parse, returns MethodCall with needs_clarification=True
        """
        self.logger.debug("Translating NL to MethodCall via LLM")

        llm_service = self.get_service("llm_service")
        prompt = get_unified_query_prompt(user_input, context)

        response = llm_service.generate(prompt=prompt, system_prompt=UNIFIED_QUERY_SYSTEM_PROMPT)

        try:
            # Parse LLM response as JSON
            data = json.loads(response)
            method_call = MethodCall(**data)

            self.logger.info(
                f"LLM translated to: {method_call.method_name}({list(method_call.parameters.keys())})"
            )
            self.logger.debug(f"Full method call: {method_call}")

            return method_call

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            self.logger.debug(f"Raw LLM response: {response}")

            return MethodCall(
                method_name="",
                needs_clarification=True,
                clarification_question=(
                    "I couldn't understand that request. Could you rephrase it?"
                ),
            )

        except TypeError as e:
            self.logger.error(f"Failed to create MethodCall from LLM data: {e}")
            self.logger.debug(f"LLM data: {data}")

            return MethodCall(
                method_name="",
                needs_clarification=True,
                clarification_question=(
                    "I understood your request but couldn't process it. "
                    "Could you try rephrasing?"
                ),
            )

    # ========================================================================
    # CONTEXT BUILDING
    # ========================================================================

    def _build_query_context(self, user_input: str) -> dict:
        """
        Build context for LLM query translation.

        Includes:
        - current_time: For relative date parsing
        - existing_tasks: For task identifier resolution (if needed)

        Args:
            state: Current agent state
            user_input: User's query

        Returns:
            Context dictionary for LLM
        """
        context = {"current_time": datetime.now().isoformat()}

        # Add existing tasks if query involves task identification
        needs_tasks = any(
            kw in user_input.lower()
            for kw in [
                "update",
                "delete",
                "start",
                "complete",
                "finish",
                "mark",
                "change",
                "modify",
                "remove",
                "cancel",
            ]
        )

        if needs_tasks:
            self.logger.debug("Query needs task context, fetching incomplete tasks")
            task_service = self.get_service("task_service")
            tasks = task_service.get_incomplete_tasks()

            context["existing_tasks"] = [
                {"id": t.id, "title": t.title, "status": t.status} for t in tasks
            ]
            self.logger.debug(f"Added {len(tasks)} tasks to context")

        return context

    # ========================================================================
    # PARAMETER CONVERSION
    # ========================================================================

    def _convert_parameter_types(self, method_call: MethodCall) -> MethodCall:
        """
        Convert parameter types from LLM output to expected types.

        Conversions:
        - ISO datetime strings → datetime objects
        - Enum values to uppercase (priority, status, energy_level)

        Args:
            method_call: MethodCall with raw LLM parameters

        Returns:
            MethodCall with converted parameter types
        """
        self.logger.debug("Converting parameter types")

        # Convert deadline strings to datetime objects
        if "deadline" in method_call.parameters:
            deadline_value = method_call.parameters["deadline"]
            if isinstance(deadline_value, str):
                try:
                    method_call.parameters["deadline"] = datetime.fromisoformat(deadline_value)
                    self.logger.debug(f"Converted deadline string to datetime: {deadline_value}")
                except (ValueError, TypeError) as e:
                    self.logger.error(f"Failed to parse deadline '{deadline_value}': {e}")
                    # Remove invalid deadline
                    del method_call.parameters["deadline"]

        # Normalize enum values to uppercase
        for enum_field in ["priority", "status", "energy_level", "estimated_energy_level"]:
            if enum_field in method_call.parameters:
                value = method_call.parameters[enum_field]
                if isinstance(value, str):
                    method_call.parameters[enum_field] = value.upper()
                    self.logger.debug(
                        f"Normalized {enum_field} to uppercase: {value} → {value.upper()}"
                    )

        return method_call

    # ========================================================================
    # TASK IDENTIFIER RESOLUTION
    # ========================================================================

    def _needs_task_resolution(self, method_call: MethodCall) -> bool:
        """
        Check if method call needs task ID resolution.

        Args:
            method_call: MethodCall to check

        Returns:
            True if task_identifier needs to be resolved to task_id
        """
        return (
            "task_identifier" in method_call.parameters and "task_id" not in method_call.parameters
        )

    def _resolve_task_identifiers(self, method_call: MethodCall, context: dict) -> MethodCall:
        """
        Resolve task_identifier to task_id using existing tasks.

        Args:
            method_call: MethodCall with task_identifier
            context: Context dict with existing_tasks

        Returns:
            Updated MethodCall with task_id (or clarification question)
        """
        identifier = method_call.parameters.get("task_identifier", "").lower()
        self.logger.debug(f"Resolving task identifier: '{identifier}'")

        # Search in existing tasks
        existing = context.get("existing_tasks", [])
        matches = [t for t in existing if identifier in t["title"].lower()]

        if len(matches) == 0:
            self.logger.warning(f"No tasks found matching '{identifier}'")
            method_call.needs_clarification = True
            method_call.clarification_question = (
                f"❌ I couldn't find a task matching '{identifier}'. "
                f"Please check the task name and try again."
            )

        elif len(matches) > 1:
            titles = [m["title"] for m in matches]
            self.logger.warning(f"Multiple tasks match '{identifier}': {titles}")
            method_call.needs_clarification = True
            method_call.clarification_question = (
                f"I found multiple tasks matching '{identifier}':\n"
                + "\n".join(f"- {title}" for title in titles)
                + "\n\nWhich one did you mean?"
            )

        else:
            # Found exactly one match
            matched_task = matches[0]
            self.logger.info(
                f"Resolved '{identifier}' to task: '{matched_task['title']}' (ID: {matched_task['id']})"
            )
            method_call.parameters["task_id"] = matched_task["id"]
            del method_call.parameters["task_identifier"]

        return method_call

    # ========================================================================
    # RESPONSE FORMATTING
    # ========================================================================

    def _format_query_result(self, result: QueryResult) -> str:
        """
        Format QueryResult into user-friendly response.

        Args:
            result: QueryResult from TaskService.query()

        Returns:
            Formatted markdown response string
        """
        if not result.success:
            self.logger.error(f"Query failed: {result.message}")
            return f"❌ **Error**: {result.message}"

        # Use message from result if available
        if result.message and result.operation_type != "READ":
            return f"✅ {result.message}"

        # Custom formatting for each operation type
        if result.operation_type == "CREATE":
            task = result.data
            response = f"✅ **Created task: {task.title}**\n\n"
            if task.description:
                response += f"Description: {task.description}\n"
            response += f"Priority: {task.priority}\n"
            response += f"Duration: {task.estimated_duration_minutes} minutes\n"
            if task.deadline:
                response += f"Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"
            return response

        elif result.operation_type == "UPDATE":
            return f"✅ {result.message}"

        elif result.operation_type == "DELETE":
            return f"✅ {result.message}"

        elif result.operation_type == "AGGREGATE":
            return result.message

        elif result.operation_type == "READ":
            tasks = result.data

            if not tasks:
                return "📋 No tasks found matching your criteria."

            response = f"📋 **Found {len(tasks)} task(s)**"

            # Add filter info if available
            if result.filters_applied:
                filters = ", ".join(f"{k}={v}" for k, v in result.filters_applied.items())
                response += f" (filters: {filters})"

            if result.sort_by:
                response += f" (sorted by {result.sort_by})"

            response += ":\n\n"

            # Format task list
            for i, task in enumerate(tasks, 1):
                response += f"{i}. **{task.title}**\n"
                if task.description:
                    response += f"   {task.description}\n"
                response += (
                    f"   Priority: {task.priority} | "
                    f"Duration: {task.estimated_duration_minutes or '?'} min"
                )
                if task.status:
                    response += f" | Status: {task.status}"
                response += "\n"
                if task.deadline:
                    response += f"   Due: {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"
                response += "\n"

            return response

        return f"✅ {result.message}"
