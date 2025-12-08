# Directory Structure

## Overview

This document details the complete project directory structure for ADHD Planner.

## Root Structure

```
adhd-planner/
├── README.md                 # Project overview
├── ARCHITECTURE.md           # System architecture
├── SETUP.md                  # Installation guide
├── pyproject.toml            # Project configuration and dependencies
├── .env.example              # Example environment configuration
├── .gitignore               # Git ignore rules
│
├── .jira/                   # Implementation stories and tracking
├── docs/                    # Documentation
├── src/                     # Source code (see below)
├── tests/                   # Test suites
├── data/                    # Runtime data (gitignored)
└── scripts/                 # Utility scripts
```

## Source Code Structure (`src/adhd_planner/`)

**Note**: The package is structured as `src/adhd_planner/` to follow Python packaging best practices. All imports use the `adhd_planner.` prefix.

```
src/
├── __init__.py              # Package marker for editable install
└── adhd_planner/            # Main package (all imports use adhd_planner.*)
    ├── __init__.py
    │
    ├── agents/              # LangGraph Agent Implementations
    │   ├── __init__.py
    │   ├── base.py          # BaseAgent abstract class
    │   ├── supervisor.py    # Main orchestrator agent
    │   ├── planning_agent.py    # Task planning and creation
    │   ├── scheduling_agent.py  # Schedule generation
    │   ├── suggestion_agent.py  # Task suggestions
    │   ├── sync_agent.py    # Sync operations
    │   └── energy_agent.py  # Energy tracking
    │
    ├── core/                # Core Application Logic
    │   ├── __init__.py
    │   ├── session_manager.py   # Session management
    │   ├── state_handler.py     # State handling
    │   └── exceptions.py    # Custom exceptions
    │
    ├── database/            # Database Layer
    │   ├── __init__.py
    │   ├── connection.py    # DB connection management
    │   ├── schema.py        # SQLAlchemy models
    │   └── migrations/      # Alembic migrations
    │       ├── alembic.ini
    │       ├── env.py
    │       └── versions/    # Migration versions
    │
    ├── graph/               # LangGraph Configuration
    │   ├── __init__.py
    │   ├── state.py         # AgentState definition
    │   ├── nodes.py         # Graph node functions
    │   ├── edges.py         # Routing/edge logic
    │   └── builder.py       # Graph construction
    │
    ├── integrations/        # External Integrations
    │   ├── __init__.py
    │   ├── apple/           # Apple Ecosystem
    │   │   ├── __init__.py
    │   │   ├── reminders.py     # Reminders API wrapper
    │   │   ├── calendar.py      # Calendar API wrapper
    │   │   └── permissions.py   # Permission handling
    │   └── llm/             # LLM Providers
    │       ├── __init__.py
    │       ├── provider_factory.py  # Factory pattern
    │       ├── ollama_provider.py
    │       ├── gemini_provider.py
    │       └── claude_provider.py
    │
    ├── models/              # Data Models (Pydantic)
    │   ├── __init__.py
    │   ├── task.py          # Task model
    │   ├── time_block.py    # TimeBlock model
    │   ├── user_preferences.py  # UserPreferences model
    │   ├── energy_log.py    # EnergyLog model
    │   ├── calendar_event.py    # CalendarEvent model
    │   ├── sync_operation.py    # SyncOperation model
    │   └── enums.py         # Enum definitions
    │
    ├── repositories/        # Data Access Layer
    │   ├── __init__.py
    │   ├── base_repository.py   # Base repository pattern
    │   ├── task_repository.py
    │   ├── time_block_repository.py
    │   ├── user_preferences_repository.py
    │   ├── energy_log_repository.py
    │   └── sync_operation_repository.py
    │
    ├── services/            # Business Logic Services
    │   ├── __init__.py
    │   ├── task_service.py      # Task CRUD and logic
    │   ├── calendar_service.py  # Time block management
    │   ├── sync_service.py      # Sync orchestration
    │   ├── llm_service.py       # LLM provider abstraction
    │   ├── energy_service.py    # Energy tracking
    │   ├── notification_service.py  # Notifications
    │   └── time_estimation_service.py  # Duration prediction
    │
    ├── ui/                  # Streamlit User Interface
    │   ├── __init__.py
    │   ├── app.py           # Main Streamlit app
    │   ├── pages/           # Streamlit pages
    │   │   ├── __init__.py
    │   │   ├── chat.py      # Chat interface
    │   │   ├── calendar_view.py # Calendar view
    │   │   ├── tasks.py     # Task management
    │   │   └── settings.py  # Settings page
    │   ├── components/      # Reusable UI components
    │   │   ├── __init__.py
    │   │   ├── task_card.py
    │   │   ├── time_block_editor.py
    │   │   ├── energy_meter.py
    │   │   └── sync_status.py
    │   └── styles/          # Custom styles
    │       └── custom.css
    │
    └── utils/               # Utilities
        ├── __init__.py
        ├── config.py        # ✅ Configuration management (ADHD-1)
        ├── logger.py        # ✅ Logging setup (ADHD-1)
        ├── time_utils.py    # Time utilities
        ├── validation.py    # Validation helpers
        └── prompts/         # LLM prompts
            ├── planning_prompts.py
            ├── scheduling_prompts.py
            └── suggestion_prompts.py
```

**Current Implementation Status**:
- ✅ = Implemented
- 🚧 = In progress
- 📋 = Planned

As of ADHD-1, only `utils/config.py` and `utils/logger.py` are implemented.

## Tests Structure (`tests/`)

```
tests/
├── __init__.py
├── conftest.py             # Pytest configuration
│
├── unit/                   # Unit tests
│   ├── __init__.py
│   ├── test_agents/
│   │   ├── test_planning_agent.py
│   │   ├── test_scheduling_agent.py
│   │   └── test_supervisor.py
│   ├── test_services/
│   │   ├── test_task_service.py
│   │   ├── test_calendar_service.py
│   │   └── test_sync_service.py
│   └── test_models/
│       ├── test_task.py
│       └── test_time_block.py
│
├── integration/            # Integration tests
│   ├── __init__.py
│   ├── test_apple_sync/
│   │   ├── test_reminders_integration.py
│   │   └── test_calendar_integration.py
│   └── test_graph_workflows/
│       ├── test_task_creation_flow.py
│       └── test_schedule_generation_flow.py
│
└── fixtures/               # Test fixtures
    ├── sample_tasks.json
    ├── sample_preferences.json
    └── mock_llm_responses.json
```

## Data Structure (`data/`)

```
data/
├── database/               # SQLite database
│   └── adhd_planner.db
│
├── config/                 # Configuration files
│   ├── default_preferences.json
│   └── prompts.yaml
│
└── logs/                   # Application logs
    ├── app.log
    ├── sync.log
    └── agents.log
```

## Scripts Structure (`scripts/`)

```
scripts/
├── setup_database.py       # Initialize database
├── test_apple_permissions.py  # Test Apple access
├── test_llm_connection.py  # Test LLM providers
├── sync_manual_trigger.py  # Manual sync trigger
└── export_data.py          # Data export utility
```

## Documentation Structure (`docs/`)

```
docs/
├── architecture/           # Architecture documentation
│   ├── system-overview.md
│   ├── agent-system.md
│   ├── data-models.md
│   └── integration-design.md
│
├── design/                 # Design documentation
│   ├── ui-specifications.md
│   ├── workflows.md
│   └── adhd-features.md
│
├── technical/              # Technical documentation
│   ├── directory-structure.md  # This file
│   ├── data-flow.md
│   ├── configuration.md
│   └── extension-guide.md
│
├── implementation/         # Implementation guides
│   ├── implementation-phases.md
│   ├── technology-choices.md
│   └── testing-strategy.md
│
├── operations/             # Operations documentation
│   ├── error-handling.md
│   ├── security-privacy.md
│   └── performance.md
│
├── user/                   # User documentation
│   ├── user-guide.md
│   └── features.md
│
└── api/                    # API documentation
    ├── data-schemas.md
    └── prompt-templates.md
```

## Key Directories Explained

### `/src/agents/`
Contains all LangGraph agent implementations. Each agent is a specialized component that handles specific aspects of the system (planning, scheduling, etc.).

### `/src/graph/`
LangGraph-specific configuration including state definition, node functions, routing logic, and graph builder.

### `/src/models/`
Pydantic models for data validation and serialization. These define the shape of data throughout the system.

### `/src/services/`
Business logic layer. Services implement domain rules and coordinate between repositories and external systems.

### `/src/repositories/`
Data access layer implementing the Repository pattern. Abstracts database operations from business logic.

### `/src/integrations/`
External system integrations (Apple, LLM providers). Wrappers around third-party APIs.

### `/src/ui/`
Streamlit-based user interface. Pages, components, and styles.

### `/src/database/`
Database schema, connection management, and migrations (Alembic).

## File Naming Conventions

- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Test files**: `test_*.py`
- **Documentation**: `kebab-case.md`

## Import Patterns

```python
# Absolute imports from src/
from src.models.task import Task
from src.services.task_service import TaskService
from src.agents.planning_agent import PlanningAgent

# Relative imports within same package
from .base import BaseAgent
from ..models.task import Task
```

## Related Documentation

- [Data Flow](data-flow.md)
- [Configuration](configuration.md)
- [Extension Guide](extension-guide.md)
