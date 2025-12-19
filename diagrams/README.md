# ADHD-Planner UML Diagrams

This folder contains auto-generated UML diagrams for the ADHD-Planner project.

## Generated Diagrams

| Diagram | Files | Description |
|---------|-------|-------------|
| **Class Diagram** | `class_diagram.png`, `.dot` | Complete class hierarchy with all models, services, agents, and relationships |
| **Component Diagram** | `component_diagram.png`, `.dot` | High-level system architecture showing layers and dependencies |
| **ER Diagram** | `er_diagram.png`, `.dot` | Database entity relationships and schema |

## Regenerating Diagrams

### Prerequisites

1. **Graphviz CLI** (macOS):
   ```bash
   brew install graphviz
   ```

2. **Python graphviz package**:
   ```bash
   pip install graphviz
   # or with uv:
   uv add graphviz
   ```

### Generate Diagrams

Run from the repository root:

```bash
python scripts/generate_class_diagram.py
```

Output files are written to `diagrams/`:
- `*.dot` - Graphviz DOT source files
- `*.png` - Rendered PNG images

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Presentation Layer                          │
│    Streamlit App → Chat | Tasks | Calendar | Settings        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                   Application Core                           │
│         ChatHandler → GraphBuilder → LangGraph Engine        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                  Multi-Agent System                          │
│   SupervisorAgent → Planning | Scheduling | Suggestion       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    Service Layer                             │
│        TaskService | CalendarService | LLMService            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                  Repository Layer                            │
│          TaskRepository | TimeBlockRepository                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                   Database Layer                             │
│            SQLAlchemy ORM → SQLite Database                  │
└─────────────────────────────────────────────────────────────┘
```

## Key Classes

| Category | Count | Examples |
|----------|-------|----------|
| Data Models | 12 | Task, TimeBlock, CalendarEvent |
| Enumerations | 8 | TaskStatus, Priority, EnergyLevel |
| ORM Models | 7 | TaskModel, TimeBlockModel |
| Repositories | 3 | BaseRepository, TaskRepository |
| Services | 6 | TaskService, CalendarService, LLMService |
| Agents | 5 | SupervisorAgent, PlanningAgent |
| Graph Components | 5 | GraphBuilder, StateManager |

## Relationship Types

The diagrams use standard UML notation:

| Arrow | Meaning |
|-------|---------|
| `──▷` (hollow) | Inheritance (extends) |
| `──◇` (hollow diamond) | Aggregation (contains) |
| `- - →` (dashed) | Dependency (uses) |
| `····→` (dotted) | Association |
| `──<` (crow's foot) | One-to-many relationship |
