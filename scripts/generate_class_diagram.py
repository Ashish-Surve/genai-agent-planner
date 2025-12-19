#!/usr/bin/env python3
"""
Generate UML Class Diagrams for ADHD-Planner using Graphviz.

This script creates visual class diagrams showing the architecture
and relationships between components in the ADHD-Planner system.

Usage:
    python scripts/generate_class_diagram.py

Requirements:
    - graphviz (Python package): pip install graphviz
    - Graphviz CLI: brew install graphviz (macOS)

Output:
    - diagrams/class_diagram.dot
    - diagrams/class_diagram.png
    - diagrams/component_diagram.dot
    - diagrams/component_diagram.png
    - diagrams/er_diagram.dot
    - diagrams/er_diagram.png
"""

from graphviz import Digraph
from pathlib import Path


def create_class_node(graph: Digraph, name: str, attributes: list[str], methods: list[str],
                      stereotype: str = None, fillcolor: str = "#FEFECE") -> None:
    """Create a UML class node with attributes and methods."""
    # Build the label using HTML-like syntax for record shape
    stereotype_row = f"«{stereotype}»\\n" if stereotype else ""

    # Format attributes
    attr_section = "\\l".join(attributes) + "\\l" if attributes else ""

    # Format methods
    method_section = "\\l".join(methods) + "\\l" if methods else ""

    # Create label with compartments
    if attr_section and method_section:
        label = f"{{{stereotype_row}{name}|{attr_section}|{method_section}}}"
    elif attr_section:
        label = f"{{{stereotype_row}{name}|{attr_section}}}"
    elif method_section:
        label = f"{{{stereotype_row}{name}||{method_section}}}"
    else:
        label = f"{{{stereotype_row}{name}}}"

    graph.node(name, label=label, shape="record", style="filled", fillcolor=fillcolor)


def create_enum_node(graph: Digraph, name: str, values: list[str], fillcolor: str = "#DDFFDD") -> None:
    """Create a UML enumeration node."""
    values_section = "\\l".join(values) + "\\l" if values else ""
    label = f"{{«enum»\\n{name}|{values_section}}}"
    graph.node(name, label=label, shape="record", style="filled", fillcolor=fillcolor)


def generate_class_diagram() -> Digraph:
    """Generate the main class diagram."""
    dot = Digraph("ADHD_Planner_Class_Diagram", comment="ADHD-Planner UML Class Diagram")

    # Graph settings
    dot.attr(rankdir="TB", splines="spline", nodesep="0.5", ranksep="1.0")
    dot.attr("node", fontname="Helvetica", fontsize="10")
    dot.attr("edge", fontname="Helvetica", fontsize="9")

    # Title
    dot.attr(label="ADHD-Planner - UML Class Diagram", labelloc="t", fontsize="16", fontname="Helvetica-Bold")

    # ====================
    # ENUMERATIONS
    # ====================
    with dot.subgraph(name="cluster_enums") as c:
        c.attr(label="Enumerations", style="dashed", color="green")

        create_enum_node(c, "TaskStatus", ["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "BLOCKED"])
        create_enum_node(c, "Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"])
        create_enum_node(c, "EnergyLevel", ["LOW", "MEDIUM", "HIGH"])
        create_enum_node(c, "BlockType", ["TASK", "BREAK", "BUFFER", "EVENT", "FREE"])
        create_enum_node(c, "SyncStatus", ["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED"])

    # ====================
    # DATA MODELS
    # ====================
    with dot.subgraph(name="cluster_models") as c:
        c.attr(label="Data Models (Pydantic)", style="dashed", color="orange")

        create_class_node(c, "BaseAppModel",
            ["+model_config: ConfigDict"],
            [],
            stereotype="abstract",
            fillcolor="#FFE4B5")

        create_class_node(c, "TimestampedModel",
            ["+created_at: datetime", "+updated_at: datetime"],
            ["+mark_updated()"],
            fillcolor="#FFE4B5")

        create_class_node(c, "Task",
            ["+id: str", "+title: str", "+description: str",
             "+estimated_duration_minutes: int", "+deadline: datetime",
             "+status: TaskStatus", "+priority: Priority",
             "+estimated_energy_level: EnergyLevel", "+requires_focus: bool",
             "+tags: list[str]"],
            ["+is_overdue: bool", "+is_completed: bool"],
            fillcolor="#FFE4B5")

        create_class_node(c, "TimeBlock",
            ["+id: str", "+task_id: str", "+start_time: datetime",
             "+end_time: datetime", "+duration_minutes: int",
             "+block_type: BlockType", "+is_flexible: bool"],
            ["+is_past: bool", "+is_current: bool"],
            fillcolor="#FFE4B5")

        create_class_node(c, "CalendarEvent",
            ["+id: str", "+title: str", "+start_time: datetime",
             "+end_time: datetime", "+source: EventSource",
             "+is_all_day: bool", "+related_task_id: str"],
            [],
            fillcolor="#FFE4B5")

        create_class_node(c, "UserPreferences",
            ["+user_id: str", "+typical_work_start: str",
             "+typical_work_end: str", "+max_focus_duration: int",
             "+llm_provider: str", "+model_name: str"],
            [],
            fillcolor="#FFE4B5")

    # ====================
    # ORM MODELS
    # ====================
    with dot.subgraph(name="cluster_orm") as c:
        c.attr(label="Database ORM (SQLAlchemy)", style="dashed", color="purple")

        create_class_node(c, "TaskModel",
            ["+id: Column[String]", "+title: Column[String]",
             "+status: Column[String]", "+priority: Column[String]",
             "+time_blocks: relationship", "+sync_operations: relationship"],
            [],
            stereotype="Entity",
            fillcolor="#E6E6FA")

        create_class_node(c, "TimeBlockModel",
            ["+id: Column[String]", "+task_id: Column[String] «FK»",
             "+start_time: Column[DateTime]", "+end_time: Column[DateTime]",
             "+task: relationship"],
            [],
            stereotype="Entity",
            fillcolor="#E6E6FA")

        create_class_node(c, "DatabaseManager",
            ["-settings: Settings", "-engine: Engine", "-session_factory: sessionmaker"],
            ["+get_session(): Session", "+create_tables()", "+drop_tables()"],
            fillcolor="#E6E6FA")

    # ====================
    # REPOSITORIES
    # ====================
    with dot.subgraph(name="cluster_repos") as c:
        c.attr(label="Repository Layer", style="dashed", color="coral")

        create_class_node(c, "BaseRepository",
            ["#model: Type[T]", "#session: Session"],
            ["+create(data): T", "+get_by_id(id): T", "+get_all(): list[T]",
             "+update(id, data): T", "+delete(id): bool", "+find_by_filters(): list[T]"],
            stereotype="Generic[T]",
            fillcolor="#FFDAB9")

        create_class_node(c, "TaskRepository",
            [],
            ["+find_by_status()", "+find_overdue()", "+find_by_priority()",
             "+find_by_energy_level()", "+search_by_title()", "+get_statistics()"],
            fillcolor="#FFDAB9")

        create_class_node(c, "TimeBlockRepository",
            [],
            ["+find_by_date()", "+find_by_date_range()", "+find_conflicts()",
             "+find_by_task()", "+get_day_statistics()"],
            fillcolor="#FFDAB9")

    # ====================
    # SERVICES
    # ====================
    with dot.subgraph(name="cluster_services") as c:
        c.attr(label="Service Layer", style="dashed", color="blue")

        create_class_node(c, "TaskService",
            ["-repository: TaskRepository", "-calendar_service: CalendarService"],
            ["+create_task()", "+update_task()", "+start_task()",
             "+complete_task()", "+delete_task()", "+list_tasks()"],
            fillcolor="#B0E0E6")

        create_class_node(c, "CalendarService",
            ["-repository: TimeBlockRepository"],
            ["+create_time_block()", "+find_available_slots()",
             "+find_conflicts()", "+get_schedule_summary()"],
            fillcolor="#B0E0E6")

        create_class_node(c, "TimeEstimationService",
            ["-task_repository: TaskRepository", "-llm_service: LLMService"],
            ["+estimate_duration(): TimeEstimate", "+calculate_estimation_accuracy()"],
            fillcolor="#B0E0E6")

        create_class_node(c, "LLMService",
            ["-provider: BaseLLMProvider"],
            ["+generate(prompt): str", "+generate_with_metadata(): LLMResponse"],
            fillcolor="#B0E0E6")

        create_class_node(c, "SettingsManager",
            ["-settings_path: Path", "-_user_settings: dict"],
            ["+get(key)", "+set(key, value)", "+save()", "+reload()"],
            fillcolor="#B0E0E6")

    # ====================
    # LLM PROVIDERS
    # ====================
    with dot.subgraph(name="cluster_llm") as c:
        c.attr(label="LLM Integration", style="dashed", color="pink")

        create_class_node(c, "BaseLLMProvider",
            ["#model_name: str", "#temperature: float"],
            ["+generate(): LLMResponse", "+is_available(): bool"],
            stereotype="abstract",
            fillcolor="#FFB6C1")

        create_class_node(c, "OllamaProvider",
            ["-base_url: str"],
            ["+generate()", "+is_available()"],
            fillcolor="#FFB6C1")

        create_class_node(c, "GeminiProvider",
            ["-api_key: str"],
            ["+generate()", "+is_available()"],
            fillcolor="#FFB6C1")

        create_class_node(c, "AnthropicProvider",
            ["-api_key: str"],
            ["+generate()", "+is_available()"],
            fillcolor="#FFB6C1")

    # ====================
    # AGENTS
    # ====================
    with dot.subgraph(name="cluster_agents") as c:
        c.attr(label="Multi-Agent System", style="dashed", color="magenta")

        create_class_node(c, "BaseAgent",
            ["#name: str", "#services: dict", "#state_manager: StateManager"],
            ["+execute(state): AgentState", "#handle_error()", "#add_response()"],
            stereotype="abstract",
            fillcolor="#DDA0DD")

        create_class_node(c, "SupervisorAgent",
            ["-llm_service: LLMService"],
            ["+execute(state)", "-_classify_and_route()"],
            fillcolor="#DDA0DD")

        create_class_node(c, "PlanningAgent",
            ["-llm_service: LLMService", "-task_service: TaskService"],
            ["+execute(state)", "-_extract_intent_and_data()", "-_create_task()"],
            fillcolor="#DDA0DD")

        create_class_node(c, "SchedulingAgent",
            ["-llm_service: LLMService", "-task_service: TaskService",
             "-calendar_service: CalendarService"],
            ["+execute(state)", "-_generate_schedule_suggestions()"],
            fillcolor="#DDA0DD")

        create_class_node(c, "SuggestionAgent",
            ["-llm_service: LLMService", "-task_service: TaskService"],
            ["+execute(state)", "-_get_task_suggestions()"],
            fillcolor="#DDA0DD")

    # ====================
    # LANGGRAPH
    # ====================
    with dot.subgraph(name="cluster_graph") as c:
        c.attr(label="LangGraph System", style="dashed", color="gold")

        create_class_node(c, "AgentState",
            ["+messages: Sequence[BaseMessage]", "+user_input: str",
             "+current_agent: str", "+routing_decision: str",
             "+context: dict", "+error: str"],
            [],
            stereotype="TypedDict",
            fillcolor="#FFFACD")

        create_class_node(c, "StateManager",
            [],
            ["+create_initial_state()", "+add_message()", "+set_routing_decision()",
             "+update_context()", "+validate_state()"],
            stereotype="static",
            fillcolor="#FFFACD")

        create_class_node(c, "GraphBuilder",
            ["-llm_service", "-task_service", "-calendar_service",
             "-agents_dict: dict", "-compiled_graph"],
            ["+build_graph(): CompiledGraph", "+invoke(user_input): dict"],
            fillcolor="#FFFACD")

        create_class_node(c, "ChatHandler",
            ["-graph: CompiledGraph"],
            ["+process_message(input, context): str", "+stream_response()"],
            fillcolor="#FFFACD")

    # ====================
    # RELATIONSHIPS
    # ====================

    # Inheritance (hollow triangle arrow)
    dot.edge("TimestampedModel", "BaseAppModel", arrowhead="onormal", label="extends")
    dot.edge("Task", "TimestampedModel", arrowhead="onormal", label="extends")
    dot.edge("TimeBlock", "BaseAppModel", arrowhead="onormal", label="extends")
    dot.edge("CalendarEvent", "BaseAppModel", arrowhead="onormal", label="extends")
    dot.edge("UserPreferences", "BaseAppModel", arrowhead="onormal", label="extends")

    dot.edge("TaskRepository", "BaseRepository", arrowhead="onormal", label="extends")
    dot.edge("TimeBlockRepository", "BaseRepository", arrowhead="onormal", label="extends")

    dot.edge("OllamaProvider", "BaseLLMProvider", arrowhead="onormal", label="extends")
    dot.edge("GeminiProvider", "BaseLLMProvider", arrowhead="onormal", label="extends")
    dot.edge("AnthropicProvider", "BaseLLMProvider", arrowhead="onormal", label="extends")

    dot.edge("SupervisorAgent", "BaseAgent", arrowhead="onormal", label="extends")
    dot.edge("PlanningAgent", "BaseAgent", arrowhead="onormal", label="extends")
    dot.edge("SchedulingAgent", "BaseAgent", arrowhead="onormal", label="extends")
    dot.edge("SuggestionAgent", "BaseAgent", arrowhead="onormal", label="extends")

    # Composition/Aggregation (diamond arrow)
    dot.edge("TaskService", "TaskRepository", arrowhead="odiamond", label="contains")
    dot.edge("TaskService", "CalendarService", arrowhead="odiamond", label="contains")
    dot.edge("CalendarService", "TimeBlockRepository", arrowhead="odiamond", label="contains")
    dot.edge("TimeEstimationService", "TaskRepository", arrowhead="odiamond", label="contains")
    dot.edge("LLMService", "BaseLLMProvider", arrowhead="odiamond", label="contains")

    # Uses/Dependencies (dashed arrow)
    dot.edge("TaskRepository", "TaskModel", style="dashed", arrowhead="vee", label="manages")
    dot.edge("TimeBlockRepository", "TimeBlockModel", style="dashed", arrowhead="vee", label="manages")

    dot.edge("GraphBuilder", "SupervisorAgent", style="dashed", arrowhead="vee", label="creates")
    dot.edge("GraphBuilder", "PlanningAgent", style="dashed", arrowhead="vee", label="creates")
    dot.edge("GraphBuilder", "SchedulingAgent", style="dashed", arrowhead="vee", label="creates")
    dot.edge("GraphBuilder", "SuggestionAgent", style="dashed", arrowhead="vee", label="creates")

    dot.edge("ChatHandler", "GraphBuilder", style="dashed", arrowhead="vee", label="uses")
    dot.edge("GraphBuilder", "AgentState", style="dashed", arrowhead="vee", label="manages")
    dot.edge("BaseAgent", "StateManager", style="dashed", arrowhead="vee", label="uses")

    dot.edge("SupervisorAgent", "LLMService", style="dashed", arrowhead="vee", label="uses")
    dot.edge("PlanningAgent", "LLMService", style="dashed", arrowhead="vee", label="uses")
    dot.edge("PlanningAgent", "TaskService", style="dashed", arrowhead="vee", label="uses")
    dot.edge("SchedulingAgent", "LLMService", style="dashed", arrowhead="vee", label="uses")
    dot.edge("SchedulingAgent", "TaskService", style="dashed", arrowhead="vee", label="uses")
    dot.edge("SchedulingAgent", "CalendarService", style="dashed", arrowhead="vee", label="uses")

    # Enum associations
    dot.edge("Task", "TaskStatus", style="dotted", arrowhead="vee")
    dot.edge("Task", "Priority", style="dotted", arrowhead="vee")
    dot.edge("Task", "EnergyLevel", style="dotted", arrowhead="vee")
    dot.edge("TimeBlock", "BlockType", style="dotted", arrowhead="vee")

    # Database relationships
    dot.edge("TaskModel", "TimeBlockModel", arrowhead="crow", arrowtail="none", label="1..*")
    dot.edge("DatabaseManager", "TaskModel", style="dashed", arrowhead="vee", label="manages")

    return dot


def generate_component_diagram() -> Digraph:
    """Generate a high-level component diagram."""
    dot = Digraph("ADHD_Planner_Component_Diagram", comment="ADHD-Planner Component Diagram")

    dot.attr(rankdir="TB", splines="spline", nodesep="0.8", ranksep="1.2")
    dot.attr("node", fontname="Helvetica", fontsize="11", shape="component")
    dot.attr("edge", fontname="Helvetica", fontsize="9")
    dot.attr(label="ADHD-Planner - Component Architecture", labelloc="t", fontsize="16", fontname="Helvetica-Bold")

    # Presentation Layer
    with dot.subgraph(name="cluster_presentation") as c:
        c.attr(label="Presentation Layer", style="filled", fillcolor="#E6F3FF")
        c.node("StreamlitApp", "Streamlit App", shape="component")
        c.node("ChatPage", "Chat Page", shape="component")
        c.node("TasksPage", "Tasks Page", shape="component")
        c.node("CalendarPage", "Calendar Page", shape="component")
        c.node("SettingsPage", "Settings Page", shape="component")

    # Application Core
    with dot.subgraph(name="cluster_core") as c:
        c.attr(label="Application Core", style="filled", fillcolor="#FFF3E6")
        c.node("ChatHandler", "ChatHandler", shape="component")
        c.node("SessionManager", "SessionManager", shape="component")
        c.node("GraphBuilder", "GraphBuilder\\n(LangGraph)", shape="component")

    # Agent Layer
    with dot.subgraph(name="cluster_agents") as c:
        c.attr(label="Multi-Agent System", style="filled", fillcolor="#F3E6FF")
        c.node("Supervisor", "SupervisorAgent", shape="component")
        c.node("Planning", "PlanningAgent", shape="component")
        c.node("Scheduling", "SchedulingAgent", shape="component")
        c.node("Suggestion", "SuggestionAgent", shape="component")

    # Service Layer
    with dot.subgraph(name="cluster_services") as c:
        c.attr(label="Service Layer", style="filled", fillcolor="#E6FFE6")
        c.node("TaskSvc", "TaskService", shape="component")
        c.node("CalendarSvc", "CalendarService", shape="component")
        c.node("LLMSvc", "LLMService", shape="component")
        c.node("SettingsMgr", "SettingsManager", shape="component")

    # Data Access Layer
    with dot.subgraph(name="cluster_data") as c:
        c.attr(label="Data Access Layer", style="filled", fillcolor="#FFE6E6")
        c.node("TaskRepo", "TaskRepository", shape="component")
        c.node("TimeBlockRepo", "TimeBlockRepository", shape="component")
        c.node("DBManager", "DatabaseManager", shape="component")

    # External
    with dot.subgraph(name="cluster_external") as c:
        c.attr(label="External", style="filled", fillcolor="#F0F0F0")
        c.node("SQLite", "SQLite DB", shape="cylinder")
        c.node("LLMAPIs", "LLM APIs\\n(Ollama/Gemini/Anthropic)", shape="box3d")

    # Relationships
    dot.edge("StreamlitApp", "ChatPage", arrowhead="none")
    dot.edge("StreamlitApp", "TasksPage", arrowhead="none")
    dot.edge("StreamlitApp", "CalendarPage", arrowhead="none")
    dot.edge("StreamlitApp", "SettingsPage", arrowhead="none")

    dot.edge("ChatPage", "ChatHandler", label="processes")
    dot.edge("ChatHandler", "GraphBuilder", label="uses")
    dot.edge("GraphBuilder", "Supervisor", label="routes to")

    dot.edge("Supervisor", "Planning", style="dashed", label="routes")
    dot.edge("Supervisor", "Scheduling", style="dashed", label="routes")
    dot.edge("Supervisor", "Suggestion", style="dashed", label="routes")

    dot.edge("Planning", "TaskSvc", label="uses")
    dot.edge("Planning", "LLMSvc", label="uses")
    dot.edge("Scheduling", "TaskSvc", label="uses")
    dot.edge("Scheduling", "CalendarSvc", label="uses")
    dot.edge("Scheduling", "LLMSvc", label="uses")

    dot.edge("TaskSvc", "TaskRepo", label="uses")
    dot.edge("CalendarSvc", "TimeBlockRepo", label="uses")
    dot.edge("TaskRepo", "DBManager", label="uses")
    dot.edge("TimeBlockRepo", "DBManager", label="uses")

    dot.edge("DBManager", "SQLite", label="connects")
    dot.edge("LLMSvc", "LLMAPIs", label="calls")

    dot.edge("SettingsPage", "SettingsMgr", label="configures")

    return dot


def generate_er_diagram() -> Digraph:
    """Generate an Entity-Relationship diagram."""
    dot = Digraph("ADHD_Planner_ER_Diagram", comment="ADHD-Planner ER Diagram")

    dot.attr(rankdir="LR", splines="spline", nodesep="0.5", ranksep="1.5")
    dot.attr("node", fontname="Helvetica", fontsize="10")
    dot.attr("edge", fontname="Helvetica", fontsize="9")
    dot.attr(label="ADHD-Planner - Entity Relationship Diagram", labelloc="t", fontsize="16", fontname="Helvetica-Bold")

    # Entity nodes using record shape
    dot.node("tasks",
        label="{tasks|id: VARCHAR(36) «PK»\\l|title: VARCHAR(200)\\l"
              "description: TEXT\\l"
              "estimated_duration_minutes: INT\\l"
              "deadline: DATETIME\\l"
              "status: VARCHAR(20)\\l"
              "priority: VARCHAR(10)\\l"
              "tags: JSON\\l"
              "...\\l}",
        shape="record", style="filled", fillcolor="#B0E0E6")

    dot.node("time_blocks",
        label="{time_blocks|id: VARCHAR(36) «PK»\\l"
              "task_id: VARCHAR(36) «FK»\\l|"
              "start_time: DATETIME\\l"
              "end_time: DATETIME\\l"
              "duration_minutes: INT\\l"
              "block_type: VARCHAR(10)\\l"
              "is_flexible: BOOLEAN\\l"
              "...\\l}",
        shape="record", style="filled", fillcolor="#FFE4B5")

    dot.node("calendar_events",
        label="{calendar_events|id: VARCHAR(36) «PK»\\l"
              "related_task_id: VARCHAR(36) «FK»\\l|"
              "title: VARCHAR(200)\\l"
              "start_time: DATETIME\\l"
              "end_time: DATETIME\\l"
              "source: VARCHAR(20)\\l"
              "is_all_day: BOOLEAN\\l"
              "...\\l}",
        shape="record", style="filled", fillcolor="#DDA0DD")

    dot.node("user_preferences",
        label="{user_preferences|id: VARCHAR(36) «PK»\\l|"
              "user_id: VARCHAR(100)\\l"
              "typical_work_start: VARCHAR(5)\\l"
              "typical_work_end: VARCHAR(5)\\l"
              "max_focus_duration: INT\\l"
              "llm_provider: VARCHAR(20)\\l"
              "...\\l}",
        shape="record", style="filled", fillcolor="#98FB98")

    dot.node("energy_logs",
        label="{energy_logs|id: VARCHAR(36) «PK»\\l|"
              "timestamp: DATETIME\\l"
              "reported_energy: VARCHAR(10)\\l"
              "predicted_energy: VARCHAR(10)\\l"
              "tasks_completed: INT\\l"
              "...\\l}",
        shape="record", style="filled", fillcolor="#F0E68C")

    dot.node("sync_operations",
        label="{sync_operations|id: VARCHAR(36) «PK»\\l"
              "task_id: VARCHAR(36) «FK»\\l|"
              "operation_type: VARCHAR(10)\\l"
              "direction: VARCHAR(20)\\l"
              "status: VARCHAR(20)\\l"
              "error_message: TEXT\\l"
              "...\\l}",
        shape="record", style="filled", fillcolor="#FFB6C1")

    dot.node("task_dependencies",
        label="{task_dependencies|task_id: VARCHAR(36) «PK,FK»\\l"
              "depends_on_id: VARCHAR(36) «PK,FK»\\l}",
        shape="record", style="filled", fillcolor="#E6E6FA")

    # Relationships with crow's foot notation approximation
    dot.edge("tasks", "time_blocks", label="1:N", arrowhead="crow", arrowtail="tee", dir="both")
    dot.edge("tasks", "calendar_events", label="1:N", arrowhead="crow", arrowtail="tee", dir="both")
    dot.edge("tasks", "sync_operations", label="1:N", arrowhead="crow", arrowtail="tee", dir="both")
    dot.edge("tasks", "task_dependencies", label="N:M\\n(self-ref)", arrowhead="crow", arrowtail="crow", dir="both")

    return dot


def main():
    """Generate all diagrams."""
    output_dir = Path("diagrams")
    output_dir.mkdir(exist_ok=True)

    print("Generating ADHD-Planner UML diagrams...")
    print("-" * 50)

    # Generate Class Diagram
    print("1. Generating Class Diagram...")
    class_diagram = generate_class_diagram()
    class_diagram.save(output_dir / "class_diagram.dot")
    class_diagram.render(output_dir / "class_diagram", format="png", cleanup=True)
    print(f"   ✓ {output_dir}/class_diagram.dot")
    print(f"   ✓ {output_dir}/class_diagram.png")

    # Generate Component Diagram
    print("2. Generating Component Diagram...")
    component_diagram = generate_component_diagram()
    component_diagram.save(output_dir / "component_diagram.dot")
    component_diagram.render(output_dir / "component_diagram", format="png", cleanup=True)
    print(f"   ✓ {output_dir}/component_diagram.dot")
    print(f"   ✓ {output_dir}/component_diagram.png")

    # Generate ER Diagram
    print("3. Generating ER Diagram...")
    er_diagram = generate_er_diagram()
    er_diagram.save(output_dir / "er_diagram.dot")
    er_diagram.render(output_dir / "er_diagram", format="png", cleanup=True)
    print(f"   ✓ {output_dir}/er_diagram.dot")
    print(f"   ✓ {output_dir}/er_diagram.png")

    print("-" * 50)
    print("All diagrams generated successfully!")
    print(f"\nOutput directory: {output_dir.absolute()}")
    print("\nFiles created:")
    for f in sorted(output_dir.iterdir()):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
