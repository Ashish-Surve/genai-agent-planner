# ADHD Planner - System Architecture

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Architectural Layers](#architectural-layers)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Key Design Patterns](#key-design-patterns)
7. [Technology Choices & Rationale](#technology-choices--rationale)
8. [Extension Points](#extension-points)

## Overview

ADHD Planner is built on a modular, layered architecture that separates concerns and enables easy extension. The system uses LangGraph for agent orchestration, supports multiple LLM providers, and integrates deeply with the Apple ecosystem while maintaining a local-first approach.

### Design Principles
- **Modularity**: Components are loosely coupled and highly cohesive
- **Extensibility**: Easy to add new agents, providers, or integrations
- **Testability**: Clear boundaries enable unit and integration testing
- **ADHD-Focused**: Every design decision considers ADHD-specific needs
- **Local-First**: Privacy and performance through local storage and processing

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT WEB UI                           │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Chat Page    │ Calendar     │ Tasks Page   │ Settings     │ │
│  │              │ View         │              │ Page         │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Session Manager & State Handler                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              LangGraph Agent Orchestrator                  │ │
│  │  ┌──────────┬──────────┬──────────┬──────────┬─────────┐  │ │
│  │  │Planning  │Scheduling│Suggestion│Sync      │Energy   │  │ │
│  │  │Agent     │Agent     │Agent     │Agent     │Tracker  │  │ │
│  │  └──────────┴──────────┴──────────┴──────────┴─────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                               │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │ Task Service │ Calendar     │ Sync Service │ LLM Service │  │
│  │              │ Service      │              │             │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
│  ┌──────────────┬──────────────┬──────────────────────────────┐ │
│  │ Energy       │ Notification │ Time Estimation              │ │
│  │ Service      │ Service      │ Service                      │ │
│  └──────────────┴──────────────┴──────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                            │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │ Repository   │ Apple        │ Cache        │ Config      │  │
│  │ Pattern      │ Integrations │ Manager      │ Manager     │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                            │
│  ┌──────────────┬──────────────┬──────────────────────────────┐ │
│  │ SQLite DB    │ JSON Config  │ Apple Reminders/Calendar     │ │
│  │              │ Files        │ (via PyObjC/EventKit)        │ │
│  └──────────────┴──────────────┴──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Architectural Layers

### 1. Presentation Layer (Streamlit UI)

**Purpose**: User interface and interaction

**Components**:
- **Chat Page**: Conversational interface with agents
- **Calendar View**: Visual time blocking and scheduling
- **Tasks Page**: Task list management
- **Settings Page**: Configuration and preferences

**Responsibilities**:
- Render UI components
- Handle user input
- Display agent responses
- Manage UI state (Streamlit session state)
- Format data for presentation

**Technologies**: Streamlit, custom CSS

### 2. Application Layer

**Purpose**: Orchestrate business logic and coordinate agents

**Components**:
- **Session Manager**: Manages user sessions and state
- **State Handler**: Maintains conversation and application state
- **LangGraph Orchestrator**: Coordinates specialized agents

**Responsibilities**:
- Route requests to appropriate agents
- Maintain conversation context
- Coordinate multi-agent workflows
- Handle application-level errors
- Manage agent lifecycle

**Technologies**: LangGraph, LangChain

### 3. Service Layer

**Purpose**: Implement business logic and provide services to agents

**Components**:
- **Task Service**: Task CRUD and business logic
- **Calendar Service**: Time block management and scheduling
- **Sync Service**: Bidirectional sync orchestration
- **LLM Service**: LLM provider abstraction
- **Energy Service**: Energy tracking and prediction
- **Notification Service**: Reminders and alerts
- **Time Estimation Service**: Duration prediction

**Responsibilities**:
- Implement business rules
- Validate data
- Coordinate between repositories
- Apply ADHD-specific logic
- Provide clean APIs to agents

**Technologies**: Python, Pydantic for validation

### 4. Data Access Layer

**Purpose**: Abstract data storage and external integrations

**Components**:
- **Repositories**: Data access using Repository pattern
- **Apple Integrations**: EventKit wrappers
- **Cache Manager**: In-memory caching
- **Config Manager**: Configuration management

**Responsibilities**:
- CRUD operations on data stores
- Query optimization
- Transaction management
- Integration with external services
- Cache management

**Technologies**: SQLAlchemy, PyObjC

### 5. Persistence Layer

**Purpose**: Store and retrieve data

**Components**:
- **SQLite Database**: Structured data storage
- **JSON Configuration**: Settings and preferences
- **Apple Reminders/Calendar**: External data sync

**Responsibilities**:
- Persist data
- Maintain data integrity
- Handle migrations
- Provide ACID guarantees (SQLite)

**Technologies**: SQLite, JSON, EventKit

## Core Components

### LangGraph Agent System

#### Supervisor Agent
- **Role**: Main orchestrator
- **Responsibilities**: Route requests, manage context, coordinate agents
- **Inputs**: User messages, conversation history
- **Outputs**: Responses to user, agent routing decisions

#### Planning Agent
- **Role**: Task creation and planning
- **Responsibilities**: Extract task details, estimate time/energy, suggest scheduling
- **Inputs**: User natural language requests
- **Outputs**: Structured task data, scheduling suggestions

#### Scheduling Agent
- **Role**: Schedule generation
- **Responsibilities**: Create ADHD-friendly schedules, optimize time blocks
- **Inputs**: Tasks, calendar events, energy patterns, preferences
- **Outputs**: Optimized schedules, time block suggestions

#### Suggestion Agent
- **Role**: Proactive recommendations
- **Responsibilities**: Suggest tasks based on context, identify opportunities
- **Inputs**: Current time, energy level, available tasks, calendar
- **Outputs**: Ranked task suggestions with reasoning

#### Sync Agent
- **Role**: Data synchronization
- **Responsibilities**: Bidirectional sync with Apple, conflict resolution
- **Inputs**: Pending sync operations, local and remote data
- **Outputs**: Sync status, resolved conflicts

#### Energy Tracking Agent
- **Role**: Energy pattern analysis
- **Responsibilities**: Track energy levels, identify patterns, predict energy
- **Inputs**: Energy logs, task completions, time data
- **Outputs**: Energy predictions, pattern insights

### Service Components

#### LLM Service
- **Provider Factory**: Creates appropriate LLM provider instance
- **Provider Implementations**: Ollama, Gemini, Claude
- **Prompt Management**: Template system for consistent prompts
- **Response Parsing**: Extract structured data from LLM responses

#### Task Service
- **CRUD Operations**: Create, read, update, delete tasks
- **Dependency Management**: Handle task relationships
- **Recurrence Handling**: Support recurring tasks
- **Status Management**: Track task lifecycle

#### Calendar Service
- **Time Block Management**: Create and manage time blocks
- **Availability Checking**: Find free time slots
- **Conflict Detection**: Identify scheduling conflicts
- **Schedule Optimization**: Apply ADHD-friendly rules

#### Sync Service
- **Queue Management**: Track pending sync operations
- **Bidirectional Sync**: Handle local ↔ Apple data flow
- **Conflict Resolution**: Resolve data conflicts
- **Status Tracking**: Monitor sync health

## Data Flow

### Task Creation Flow

```
User: "Add task: write report, 2 hours"
         │
         ▼
   [Streamlit Chat UI]
         │
         ▼
   [Session Manager]
         │
         ▼
[LangGraph Supervisor Agent]
         │
         ▼
  [Planning Agent]
         │
         ├──► [LLM Service] ──► Extract details
         │
         ├──► [Time Estimation Service] ──► Estimate duration
         │
         ├──► [Energy Service] ──► Assess energy needs
         │
         └──► [Calendar Service] ──► Check availability
         │
         ▼
   [Task Service] ──► Validate and create task
         │
         ▼
 [Task Repository] ──► Save to database
         │
         ▼
   [Sync Service] ──► Queue for Apple sync (if enabled)
         │
         ▼
[Supervisor Agent] ──► Respond to user
         │
         ▼
      [UI] ──► Display confirmation
```

### Schedule Generation Flow

```
User: "Plan my day"
         │
         ▼
[Supervisor Agent]
         │
         ▼
[Scheduling Agent]
         │
         ├──► [Task Service] ──► Get incomplete tasks
         │
         ├──► [Calendar Service] ──► Get existing events
         │
         ├──► [Energy Service] ──► Get energy patterns
         │
         ├──► [Config Manager] ──► Get user preferences
         │
         ▼
   [LLM Service] ──► Generate schedule options
         │
         ▼
[Apply ADHD Rules]
  - Add buffer time
  - Group similar tasks
  - Match energy levels
  - Minimize context switches
         │
         ▼
  [Present Options] ──► Show to user
         │
         ▼
 [User Selects] ──► Choose schedule
         │
         ├──► [Calendar Service] ──► Create time blocks
         │
         ├──► [Task Service] ──► Update task scheduling
         │
         └──► [Sync Service] ──► Sync to Apple (if enabled)
```

### Bidirectional Sync Flow

```
LOCAL → APPLE:
  Task modified locally
         │
         ▼
   [Task Service] ──► Update task
         │
         ▼
   [Sync Service] ──► Detect change
         │
         ▼
IF sync_enabled:
   [Sync Agent] ──► Create sync operation
         │
         ▼
[Apple Integration] ──► Update Reminder/Calendar
         │
         ▼
 [Update Metadata] ──► Record sync timestamp

APPLE → LOCAL:
  [Sync Service] ──► Poll Apple (periodic)
         │
         ▼
[Apple Integration] ──► Fetch changes
         │
         ▼
   [Sync Service] ──► Compare timestamps
         │
         ▼
  IF conflict:
    [Conflict Resolution] ──► Last-write-wins or user prompt
  ELSE:
    [Task Service] ──► Update local task
         │
         ▼
 [Update Metadata] ──► Record sync timestamp
```

## Key Design Patterns

### 1. Supervisor Pattern (Agent Coordination)

**Purpose**: Coordinate multiple specialized agents

**Implementation**:
- Supervisor agent routes requests to appropriate specialists
- Maintains conversation context
- Handles multi-turn interactions
- Manages error recovery

**Benefits**:
- Clear separation of agent responsibilities
- Easy to add new specialized agents
- Centralized routing logic
- Better error handling

### 2. Repository Pattern (Data Access)

**Purpose**: Abstract data storage implementation

**Implementation**:
- Base repository with common CRUD operations
- Specialized repositories for each entity
- Repositories use SQLAlchemy for database access

**Benefits**:
- Testability (easy to mock)
- Swappable data sources
- DRY (don't repeat yourself)
- Clear data access APIs

### 3. Factory Pattern (LLM Providers)

**Purpose**: Create provider instances based on configuration

**Implementation**:
- `LLMProviderFactory.create(provider_name, **config)`
- Provider implementations share common interface
- Configuration-driven provider selection

**Benefits**:
- Runtime provider switching
- Easy to add new providers
- Consistent LLM interface
- Testing with mock providers

### 4. Strategy Pattern (Sync Strategies)

**Purpose**: Different sync behaviors based on configuration

**Implementation**:
- One-way (Local → Apple)
- One-way (Apple → Local)
- Two-way (bidirectional)
- Per-item sync toggle

**Benefits**:
- Flexible sync behavior
- Easy to add new strategies
- User control over sync
- Simplified testing

### 5. Observer Pattern (Event Handling)

**Purpose**: React to data changes and trigger actions

**Implementation**:
- Task changes trigger sync operations
- Energy logs trigger pattern analysis
- Schedule changes trigger notifications

**Benefits**:
- Loose coupling between components
- Easy to add new reactions
- Clear event flow
- Maintainable code

## Technology Choices & Rationale

### Why LangGraph?

**Chosen**: LangGraph for agent orchestration

**Rationale**:
- **Structured Workflows**: Clear state management and flow control
- **Extensibility**: Easy to add agent nodes without refactoring
- **Debugging**: Graph structure makes workflows visible and debuggable
- **LangChain Integration**: Seamless LLM provider integration
- **Best Practice**: Industry-standard tool for multi-agent systems

**Alternatives Considered**:
- CrewAI: Less flexible for custom workflows
- AutoGen: More complex setup, steeper learning curve
- Custom Framework: Would require significant development effort

### Why Supervisor Pattern?

**Chosen**: Supervisor agent coordinating specialists

**Rationale**:
- **Separation of Concerns**: Each agent has focused responsibility
- **Flexibility**: Easy routing based on request type
- **Scalability**: Add agents without modifying existing ones
- **Error Handling**: Centralized failure management
- **Context Management**: Single point for conversation state

**Alternatives Considered**:
- Flat Architecture: Would lead to complex, monolithic agents
- Chain Pattern: Less flexible for branching logic

### Why Local-First with SQLite?

**Chosen**: SQLite for local data storage

**Rationale**:
- **Privacy**: Data never leaves user's device
- **Performance**: No network latency
- **Simplicity**: No server setup required
- **Reliability**: Works offline
- **Portability**: Easy backup and transfer

**Alternatives Considered**:
- PostgreSQL: Overkill for single-user, local app
- Cloud Database: Privacy concerns, requires internet
- JSON Files: Harder to query, no ACID guarantees

### Why Per-Item Sync Toggle?

**Chosen**: Optional sync on per-task basis

**Rationale**:
- **ADHD-Friendly**: Reduces decision fatigue with smart defaults
- **Flexibility**: Some tasks are private, some are collaborative
- **Experimentation**: Try different workflows
- **Privacy**: Keep sensitive tasks local
- **Performance**: Reduce sync overhead

**Alternatives Considered**:
- All-or-Nothing: Too rigid, not ADHD-friendly
- Folder-Based: Apple Reminders limited folder support

### Why Multiple LLM Providers?

**Chosen**: Configurable Ollama/Gemini/Claude support

**Rationale**:
- **Cost Control**: Ollama is free and local
- **Quality Options**: Claude/Gemini for better results when needed
- **Privacy Options**: Ollama for sensitive data
- **Flexibility**: Switch based on task or availability
- **Future-Proof**: Easy to add new providers

**Alternatives Considered**:
- Single Provider: Less flexible, vendor lock-in
- OpenAI Only: Cost concerns for some users

## Extension Points

### Adding New Agents

1. Create agent class extending `BaseAgent`
2. Implement `execute()` and `should_handle()` methods
3. Add node to LangGraph builder
4. Update supervisor routing logic
5. (Optional) Update state schema if needed

**Example Use Cases**:
- Habit Tracking Agent
- Goal Setting Agent
- Focus Mode Agent
- Review/Reflection Agent

### Adding New LLM Providers

1. Implement `LLMProvider` interface
2. Add to `LLMProviderFactory`
3. Add configuration in settings
4. Update UI and documentation

**Example Providers**:
- OpenAI GPT
- Local models via LM Studio
- Azure OpenAI
- Open-source alternatives

### Adding New Sync Integrations

1. Create integration module in `integrations/`
2. Implement sync methods matching interface
3. Add to `SyncService` routing
4. Add configuration options
5. Update UI with sync controls

**Example Integrations**:
- Google Calendar/Tasks
- Microsoft To Do
- Notion
- Todoist
- Linear/Jira

### Adding New UI Pages

1. Create page in `ui/pages/`
2. Add routing in main app
3. Create necessary components
4. Update navigation

**Example Pages**:
- Analytics Dashboard
- Habit Tracker
- Focus Timer
- Weekly Review
- Goal Board

### Making Framework Reusable

**Extractable Components**:

1. **LangGraph Agent Framework**
   - Base agent classes
   - Supervisor pattern implementation
   - State management utilities
   - Graph builder tools

2. **LLM Service Layer**
   - Provider abstraction
   - Factory pattern
   - Prompt management
   - Response parsing

3. **Repository Pattern**
   - Base repository
   - SQLAlchemy utilities
   - Migration helpers

4. **Streamlit Components**
   - Reusable UI components
   - Session management patterns
   - State handling utilities

**How to Extract**:
- Package as separate Python libraries
- Use dependency injection
- Provide clear interfaces
- Include documentation and examples
- Maintain backward compatibility

## System Qualities

### Scalability
- **Current**: Single user, local storage
- **Future**: Can migrate to PostgreSQL for multi-user
- **Agents**: Can distribute to separate processes if needed

### Performance
- **Database**: Indexed queries, connection pooling
- **LLM**: Caching, streaming responses
- **Sync**: Debounced updates, incremental sync
- **UI**: Streamlit caching, lazy loading

### Reliability
- **Error Handling**: Retry logic, graceful degradation
- **Data Integrity**: ACID guarantees, validation layers
- **Sync**: Conflict resolution, status tracking
- **Logging**: Comprehensive logging for debugging

### Maintainability
- **Modularity**: Clear component boundaries
- **Documentation**: Comprehensive inline and external docs
- **Testing**: Unit, integration, and UI tests
- **Standards**: Consistent coding patterns

### Security & Privacy
- **Local-First**: Data stays on device
- **API Keys**: Stored in env files, never committed
- **Validation**: Multiple validation layers
- **Permissions**: Minimal Apple permissions requested

## References

For more detailed information, see:
- [Agent System Design](docs/architecture/agent-system.md)
- [Data Models](docs/architecture/data-models.md)
- [Integration Design](docs/architecture/integration-design.md)
- [Extension Guide](docs/technical/extension-guide.md)
- [Implementation Phases](docs/implementation/implementation-phases.md)
