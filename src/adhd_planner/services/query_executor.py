"""Query execution utilities for sorting, pagination, and aggregation."""

from collections import defaultdict
from datetime import datetime
from typing import Any

from adhd_planner.database.schema import TaskModel
from adhd_planner.utils.logger import get_logger

logger = get_logger("query_executor")


class QueryExecutor:
    """Executes query operations (sorting, aggregation, pagination)."""

    # Priority order for sorting (lower number = higher priority)
    PRIORITY_ORDER = {"URGENT": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    # Energy level order for sorting (lower number = higher energy)
    ENERGY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

    # Status order for sorting
    STATUS_ORDER = {"IN_PROGRESS": 0, "NOT_STARTED": 1, "BLOCKED": 2, "COMPLETED": 3}

    def apply_sorting(
        self, tasks: list[TaskModel], sort_by: str, sort_order: str
    ) -> list[TaskModel]:
        """
        Apply sorting to task list.

        Args:
            tasks: List of tasks to sort
            sort_by: Field to sort by
            sort_order: "asc" or "desc"

        Returns:
            Sorted list of tasks
        """
        logger.debug(f"Sorting {len(tasks)} tasks by {sort_by} ({sort_order})")

        sort_keys = {
            "priority": lambda t: self.PRIORITY_ORDER.get(t.priority, 99),
            "deadline": lambda t: t.deadline or datetime.max,
            "created_at": lambda t: t.created_at,
            "updated_at": lambda t: t.updated_at,
            "title": lambda t: t.title.lower(),
            "energy_level": lambda t: self.ENERGY_ORDER.get(t.estimated_energy_level, 99),
            "duration": lambda t: t.estimated_duration_minutes or 0,
            "status": lambda t: self.STATUS_ORDER.get(t.status, 99),
        }

        key_func = sort_keys.get(sort_by)
        if not key_func:
            logger.warning(f"Unknown sort field: {sort_by}, skipping sort")
            return tasks

        reverse = sort_order == "desc"
        sorted_tasks = sorted(tasks, key=key_func, reverse=reverse)

        logger.debug(f"Sorted tasks by {sort_by} {sort_order}")
        return sorted_tasks

    def apply_pagination(
        self, tasks: list[TaskModel], limit: int | None, offset: int | None
    ) -> list[TaskModel]:
        """
        Apply pagination to task list.

        Args:
            tasks: List of tasks to paginate
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            Paginated list of tasks
        """
        original_count = len(tasks)

        if offset:
            tasks = tasks[offset:]
            logger.debug(f"Applied offset {offset}, remaining: {len(tasks)}")

        if limit:
            tasks = tasks[:limit]
            logger.debug(f"Applied limit {limit}, result: {len(tasks)}")

        logger.debug(f"Pagination result: {len(tasks)} tasks (from {original_count} total)")
        return tasks

    def apply_aggregation(
        self, tasks: list[TaskModel], aggregate: str, group_by: str | None
    ) -> dict[str, Any]:
        """
        Apply aggregation operations.

        Args:
            tasks: List of tasks to aggregate
            aggregate: Type of aggregation ("count", "group_by")
            group_by: Field to group by (for group_by aggregation)

        Returns:
            Dictionary with aggregation results
        """
        logger.debug(
            f"Applying aggregation: {aggregate}, group_by: {group_by} on {len(tasks)} tasks"
        )

        if aggregate == "count":
            result = {"count": len(tasks)}
            logger.info(f"Count aggregation result: {result['count']}")
            return result

        if aggregate == "group_by" and group_by:
            groups: dict[str, list[TaskModel]] = defaultdict(list)

            for task in tasks:
                key = getattr(task, group_by, "unknown")
                groups[str(key)].append(task)

            result = {"groups": {k: {"count": len(v), "tasks": v} for k, v in groups.items()}}

            logger.info(f"Group by {group_by} result: {len(result['groups'])} groups")
            return result

        logger.warning(f"Unknown aggregation type: {aggregate}")
        return {}

    def format_aggregation_message(self, aggregation_result: dict) -> str:
        """
        Format aggregation result into user-friendly message.

        Args:
            aggregation_result: Result from apply_aggregation

        Returns:
            Formatted message string
        """
        if "count" in aggregation_result:
            return f"📊 Total count: {aggregation_result['count']}"

        if "groups" in aggregation_result:
            groups = aggregation_result["groups"]
            message = f"📊 **Grouped Results** ({len(groups)} groups):\n\n"

            for group_name, group_data in groups.items():
                message += f"**{group_name}**: {group_data['count']} tasks\n"

            return message

        return "Aggregation complete"
