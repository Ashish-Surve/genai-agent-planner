"""Validation logic for method calls from LLM."""

from adhd_planner.services.query_models import MethodCall
from adhd_planner.utils.logger import get_logger

logger = get_logger("query_validator")


class MethodCallValidator:
    """Validates LLM-generated method calls before execution."""

    # Valid TaskService method names
    VALID_METHODS = {
        "create_task",
        "update_task",
        "delete_task",
        "get_task",
        "list_tasks",
        "get_tasks_by_status",
        "get_overdue_tasks",
        "get_tasks_ready_to_start",
        "get_incomplete_tasks",
        "start_task",
        "complete_task",
        "search_by_title",
        "find_by_energy_level",
        "get_statistics",
        "find_due_soon",
    }

    # Required parameters for each method
    REQUIRED_PARAMS = {
        "create_task": ["title"],
        "update_task": ["task_id"],
        "delete_task": ["task_id"],
        "get_task": ["task_id"],
        "start_task": ["task_id"],
        "complete_task": ["task_id"],
        "search_by_title": ["query"],
        "find_by_energy_level": ["energy_level"],
        "get_tasks_by_status": ["status"],
        "find_due_soon": [],
    }

    # Valid parameters for each method (prevents invalid kwargs errors)
    VALID_PARAMS = {
        "create_task": [
            "title",
            "description",
            "estimated_duration_minutes",
            "energy_level",
            "priority",
            "deadline",
            "context_category",
            "requires_focus",
            "tags",
            "dependency_ids",
            "sync_enabled",
        ],
        "update_task": [
            "task_id",
            "task_identifier",
            "title",
            "description",
            "priority",
            "deadline",
            "status",
            "energy_level",
            "context_category",
            "requires_focus",
            "tags",
            "estimated_duration_minutes",
        ],
        "delete_task": ["task_id", "task_identifier"],
        "get_task": ["task_id", "task_identifier"],
        "list_tasks": ["status", "priority", "context_category", "tag", "overdue_only", "limit"],
        "get_tasks_by_status": ["status"],
        "get_overdue_tasks": [],
        "get_tasks_ready_to_start": [],
        "get_incomplete_tasks": [],
        "start_task": ["task_id", "task_identifier"],
        "complete_task": ["task_id", "task_identifier", "actual_duration_minutes"],
        "search_by_title": ["query"],
        "find_by_energy_level": ["energy_level"],
        "get_statistics": [],
        "find_due_soon": ["hours"],
    }

    # Valid enum values
    VALID_PRIORITIES = {"URGENT", "HIGH", "MEDIUM", "LOW"}
    VALID_STATUSES = {"NOT_STARTED", "IN_PROGRESS", "COMPLETED", "BLOCKED"}
    VALID_ENERGY_LEVELS = {"LOW", "MEDIUM", "HIGH"}

    def validate(self, method_call: MethodCall) -> tuple[bool, str | None]:
        """
        Validate method call structure and parameters.

        Args:
            method_call: MethodCall to validate

        Returns:
            (is_valid, error_message)
            - is_valid: True if valid, False otherwise
            - error_message: Description of validation error (None if valid)
        """
        logger.debug(f"Validating method call: {method_call.method_name}")

        # 1. Validate method name exists
        if method_call.method_name not in self.VALID_METHODS:
            error = f"Invalid method name: {method_call.method_name}. Valid methods are: {', '.join(sorted(self.VALID_METHODS))}"
            logger.warning(error)
            return False, error

        # 2. Validate required parameters are present
        required_params = self.REQUIRED_PARAMS.get(method_call.method_name, [])
        for param in required_params:
            # Allow task_identifier as an alternative to task_id (will be resolved later)
            if param == "task_id" and "task_identifier" in method_call.parameters:
                continue

            if param not in method_call.parameters:
                error = (
                    f"Missing required parameter '{param}' for method '{method_call.method_name}'"
                )
                logger.warning(error)
                return False, error

        # 3. Validate no invalid parameters are passed
        valid_params = self.VALID_PARAMS.get(method_call.method_name, None)
        if valid_params is not None:
            for param in method_call.parameters:
                if param not in valid_params:
                    error = (
                        f"Invalid parameter '{param}' for method '{method_call.method_name}'. "
                        f"Valid parameters are: {', '.join(valid_params) if valid_params else 'none'}"
                    )
                    logger.warning(error)
                    return False, error

        # 4. Validate enum values
        validation_result = self._validate_enum_values(method_call)
        if not validation_result[0]:
            return validation_result

        # 5. Validate sort parameters
        if method_call.sort_by:
            valid_sort_fields = {
                "priority",
                "deadline",
                "created_at",
                "updated_at",
                "title",
                "energy_level",
                "duration",
                "status",
            }
            if method_call.sort_by not in valid_sort_fields:
                error = f"Invalid sort_by field: {method_call.sort_by}. Valid fields are: {', '.join(sorted(valid_sort_fields))}"
                logger.warning(error)
                return False, error

            if method_call.sort_order not in ["asc", "desc"]:
                error = f"Invalid sort_order: {method_call.sort_order}. Must be 'asc' or 'desc'"
                logger.warning(error)
                return False, error

        # 6. Validate aggregation parameters
        if method_call.aggregate:
            valid_aggregates = {"count", "group_by"}
            if method_call.aggregate not in valid_aggregates:
                error = f"Invalid aggregate: {method_call.aggregate}. Valid aggregates are: {', '.join(sorted(valid_aggregates))}"
                logger.warning(error)
                return False, error

            if method_call.aggregate == "group_by" and not method_call.group_by:
                error = "group_by aggregate requires group_by field to be specified"
                logger.warning(error)
                return False, error

        logger.debug(f"Method call validation passed: {method_call.method_name}")
        return True, None

    def _validate_enum_values(self, method_call: MethodCall) -> tuple[bool, str | None]:
        """
        Validate enum parameter values.

        Args:
            method_call: MethodCall to validate

        Returns:
            (is_valid, error_message)
        """
        # Validate priority
        if "priority" in method_call.parameters:
            priority = method_call.parameters["priority"]
            if priority not in self.VALID_PRIORITIES:
                error = f"Invalid priority: {priority}. Valid values are: {', '.join(sorted(self.VALID_PRIORITIES))}"
                logger.warning(error)
                return False, error

        # Validate status
        if "status" in method_call.parameters:
            status = method_call.parameters["status"]
            if status not in self.VALID_STATUSES:
                error = f"Invalid status: {status}. Valid values are: {', '.join(sorted(self.VALID_STATUSES))}"
                logger.warning(error)
                return False, error

        # Validate energy_level
        if "energy_level" in method_call.parameters:
            energy = method_call.parameters["energy_level"]
            if energy not in self.VALID_ENERGY_LEVELS:
                error = f"Invalid energy_level: {energy}. Valid values are: {', '.join(sorted(self.VALID_ENERGY_LEVELS))}"
                logger.warning(error)
                return False, error

        # Validate estimated_energy_level (alternative naming)
        if "estimated_energy_level" in method_call.parameters:
            energy = method_call.parameters["estimated_energy_level"]
            if energy not in self.VALID_ENERGY_LEVELS:
                error = f"Invalid estimated_energy_level: {energy}. Valid values are: {', '.join(sorted(self.VALID_ENERGY_LEVELS))}"
                logger.warning(error)
                return False, error

        return True, None

    def find_similar_methods(self, invalid_method: str) -> list[str]:
        """
        Find similar method names for error messages.

        Args:
            invalid_method: The invalid method name

        Returns:
            List of similar valid method names
        """
        # Simple similarity: contains common substring
        similar = []
        invalid_lower = invalid_method.lower()

        for valid_method in self.VALID_METHODS:
            # Check if they share a significant substring
            if len(invalid_lower) >= 3:
                if invalid_lower[:3] in valid_method.lower():
                    similar.append(valid_method)

        return similar[:3]  # Return max 3 suggestions
