"""Data models for unified query interface."""

from dataclasses import dataclass, field
from typing import Any

from adhd_planner.database.schema import TaskModel


@dataclass
class MethodCall:
    """
    Structured representation of TaskService method to call.

    This is the output from LLM translation of natural language queries.
    It specifies which method to call, with what parameters, and any
    post-processing instructions (sorting, pagination, aggregation).
    """

    # Method identification
    method_name: str  # e.g., "list_tasks", "create_task", "get_statistics"

    # Parameters for the method
    parameters: dict[str, Any] = field(default_factory=dict)

    # Post-processing instructions for list results
    sort_by: str | None = None  # "priority", "deadline", "created_at", "title", "energy_level"
    sort_order: str = "asc"  # "asc" or "desc"
    limit: int | None = None  # Pagination limit
    offset: int | None = None  # Pagination offset

    # Aggregation instructions
    aggregate: str | None = None  # "count", "group_by"
    group_by: str | None = None  # Field to group by

    # Clarification handling
    needs_clarification: bool = False
    clarification_question: str | None = None


@dataclass
class QueryResult:
    """
    Result of a query operation from TaskService.query().

    Standardized response format for all task operations,
    including metadata about the operation and formatted results.
    """

    # Operation metadata
    operation_type: str  # "CREATE", "UPDATE", "DELETE", "READ", "AGGREGATE", "ERROR"
    success: bool

    # Data (type varies by operation)
    data: list[TaskModel] | TaskModel | dict | int | None

    # Metadata for list results
    total_count: int | None = None
    filters_applied: dict | None = None
    sort_by: str | None = None

    # Aggregation results
    aggregations: dict | None = None

    # User-facing message
    message: str = ""

    # Clarification needs
    needs_clarification: bool = False
    clarification_question: str | None = None
