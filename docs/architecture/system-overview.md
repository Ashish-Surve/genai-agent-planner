# System Overview

## Purpose

This document provides a high-level overview of the ADHD Planner system architecture, describing the major components, their responsibilities, and how they interact.

## Architecture Diagram

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

## Layer Responsibilities

### Presentation Layer (Streamlit UI)
**Purpose**: User interface and user interaction

**Key Components**:
- Chat Page - conversational interface with agents
- Calendar View - visual time blocking and scheduling
- Tasks Page - task list management
- Settings Page - configuration and preferences

**Responsibilities**:
- Render UI components
- Handle user input events
- Display agent responses and data
- Manage UI-specific state

### Application Layer
**Purpose**: Business logic orchestration and agent coordination

**Key Components**:
- Session Manager - manages user sessions
- State Handler - maintains conversation and application state
- LangGraph Orchestrator - coordinates specialized AI agents

**Responsibilities**:
- Route user requests to appropriate agents
- Maintain conversation context
- Coordinate multi-agent workflows
- Handle application-level errors
- Manage agent lifecycle

### Service Layer
**Purpose**: Implement domain logic and provide services to agents

**Key Components**:
- Task Service - task CRUD and business rules
- Calendar Service - time block management
- Sync Service - bidirectional sync with Apple
- LLM Service - LLM provider abstraction
- Energy Service - energy tracking and prediction
- Notification Service - reminders and alerts
- Time Estimation Service - duration prediction

**Responsibilities**:
- Implement business rules
- Validate data according to domain constraints
- Coordinate between repositories
- Apply ADHD-specific logic
- Provide clean APIs to agents

### Data Access Layer
**Purpose**: Abstract data storage and external integrations

**Key Components**:
- Repositories - data access using Repository pattern
- Apple Integrations - EventKit wrappers for Reminders/Calendar
- Cache Manager - in-memory caching
- Config Manager - configuration management

**Responsibilities**:
- CRUD operations on data stores
- Query optimization
- Transaction management
- Integration with external services
- Cache invalidation and management

### Persistence Layer
**Purpose**: Store and retrieve data

**Key Components**:
- SQLite Database - structured local storage
- JSON Configuration - settings and user preferences
- Apple Reminders/Calendar - external sync targets

**Responsibilities**:
- Persist data to disk
- Maintain data integrity
- Handle schema migrations
- Provide ACID guarantees

## Data Flow Example

### Task Creation Flow

```
User Input: "Add task: write report, 2 hours"
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
      ├──► [LLM Service] ──► Parse natural language
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
[Task Repository] ──► Save to SQLite
      │
      ▼
[Sync Service] ──► Queue for Apple sync (if enabled)
      │
      ▼
[Supervisor Agent] ──► Format response
      │
      ▼
[Streamlit UI] ──► Display confirmation
```

## Key Design Patterns

### 1. Layered Architecture
- Clear separation of concerns across 5 layers
- Each layer only depends on layers below it
- Enables independent testing and modification

### 2. Supervisor Pattern (Multi-Agent)
- Central supervisor coordinates specialized agents
- Each agent has a focused responsibility
- Flexible routing based on request context

### 3. Repository Pattern (Data Access)
- Abstract data storage implementation
- Consistent interface for data operations
- Easy to mock for testing

### 4. Factory Pattern (LLM Providers)
- Runtime provider selection
- Consistent interface across providers
- Easy to add new LLM providers

### 5. Strategy Pattern (Sync Behavior)
- Configurable sync strategies
- Per-item sync control
- Flexible bidirectional sync

## Component Interactions

### Agent → Service → Repository Flow

```
┌─────────────┐
│   Agent     │ ─────┐
└─────────────┘      │
                     │ Calls service methods
                     ▼
              ┌─────────────┐
              │   Service   │ ─────┐
              └─────────────┘      │
                                   │ Uses repository
                                   ▼
                            ┌─────────────┐
                            │ Repository  │
                            └─────────────┘
                                   │
                                   │ Persists to
                                   ▼
                            ┌─────────────┐
                            │  Database   │
                            └─────────────┘
```

### Bidirectional Sync Flow

```
Local Change                    Apple Change
      │                              │
      ▼                              ▼
[Sync Service] ◄──────────────► [Sync Service]
      │                              │
      ├─► Queue operation            ├─► Detect change
      │                              │
      ▼                              ▼
[Sync Agent]                   [Sync Agent]
      │                              │
      ▼                              ▼
[Apple Integration]            [Apple Integration]
      │                              │
      └──► Update Reminder      ◄────┘ Fetch changes
```

## Technology Stack

### Core Technologies
- **UI Framework**: Streamlit 1.39+
- **Agent Framework**: LangGraph 0.2+
- **LLM Integration**: LangChain 0.3+
- **Database**: SQLite with SQLAlchemy 2.0+
- **Apple Integration**: PyObjC + EventKit

### LLM Providers (Configurable)
- **Ollama**: Local, free, privacy-focused
- **Google Gemini**: API-based, good balance
- **Anthropic Claude**: API-based, highest quality

## System Qualities

### Scalability
- Current: Single-user, local deployment
- Future: Can scale to multi-user with PostgreSQL
- Agents can be distributed across processes if needed

### Performance
- Local-first: No network latency for core operations
- Indexed database queries
- LLM response caching
- Debounced sync operations

### Reliability
- ACID guarantees from SQLite
- Retry logic for LLM and sync operations
- Comprehensive error handling
- Graceful degradation when services unavailable

### Maintainability
- Clear component boundaries
- Consistent coding patterns
- Comprehensive documentation
- Extensive logging

### Security & Privacy
- Local-first architecture (data stays on device)
- API keys stored in environment variables
- No cloud storage required
- Minimal Apple permissions requested

## Extension Points

The architecture supports extension through:

1. **New Agents**: Add specialized agents to the LangGraph graph
2. **New Services**: Implement new business logic services
3. **New Integrations**: Add sync with other platforms (Google, Microsoft, etc.)
4. **New UI Pages**: Extend Streamlit UI with additional views
5. **New LLM Providers**: Implement provider interface for new LLMs

## Related Documentation

- [Agent System Design](agent-system.md) - Detailed agent workflows
- [Data Models](data-models.md) - Entity schemas and relationships
- [Integration Design](integration-design.md) - Apple and LLM integration details
- [Extension Guide](../technical/extension-guide.md) - How to extend the system
