# Agent System Design

## Overview

The ADHD Planner uses a multi-agent architecture built on LangGraph, where specialized AI agents collaborate to handle different aspects of task planning and management. This document describes the agent system design, workflows, and coordination mechanisms.

## Table of Contents
1. [Agent Architecture](#agent-architecture)
2. [Agent State Schema](#agent-state-schema)
3. [Specialized Agents](#specialized-agents)
4. [Agent Workflows](#agent-workflows)
5. [LangGraph Implementation](#langgraph-implementation)
6. [Agent Coordination](#agent-coordination)

## Agent Architecture

### Supervisor Pattern

The system uses a **supervisor pattern** where a main orchestrator coordinates specialized sub-agents:

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN ORCHESTRATOR                        │
│                   (Supervisor Agent)                        │
│                                                             │
│  Responsibilities:                                          │
│  - Route user requests to appropriate agents               │
│  - Manage conversation context                             │
│  - Coordinate multi-agent workflows                         │
│  - Handle error recovery                                    │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ Routes to:
               │
    ┌──────────┴──────────┬────────────┬────────────┬────────────┐
    ▼                     ▼            ▼            ▼            ▼
┌────────┐          ┌──────────┐  ┌──────────┐ ┌──────────┐ ┌──────────┐
│Planning│          │Scheduling│  │Suggestion│ │   Sync   │ │  Energy  │
│ Agent  │          │  Agent   │  │  Agent   │ │  Agent   │ │  Agent   │
└────────┘          └──────────┘  └──────────┘ └──────────┘ └──────────┘
```

### Design Rationale

**Why Supervisor Pattern?**
- **Separation of Concerns**: Each agent has a focused responsibility
- **Flexibility**: Easy to route based on context
- **Extensibility**: Add new agents without modifying existing ones
- **Error Handling**: Centralized failure management
- **Context Management**: Single point for conversation state

## Agent State Schema

### AgentState Definition

The shared state passed between all agents:

```python
class AgentState(TypedDict):
    """Shared state across all agents in the graph"""

    # Conversation Management
    messages: List[BaseMessage]          # Chat history
    user_input: str                       # Current user message
    agent_response: str                   # Agent's response

    # Task Context
    current_task: Optional[Task]          # Task being worked on
    tasks_in_context: List[Task]          # Relevant tasks

    # Calendar Context
    current_date: datetime                # Current date/time
    time_blocks: List[TimeBlock]          # Scheduled blocks
    calendar_events: List[CalendarEvent]  # Existing events

    # User Context
    user_preferences: UserPreferences     # User settings
    current_energy_level: EnergyLevel     # Predicted energy
    recent_context_switches: int          # Switch count

    # Agent Coordination
    active_agent: str                     # Currently active agent
    agent_history: List[str]              # Agent execution sequence
    needs_clarification: bool             # Requires user input

    # Sync Status
    pending_syncs: List[SyncOperation]    # Queued sync operations
    last_sync_timestamp: datetime         # Last successful sync
```

### State Lifecycle

```
User Request
     ↓
Initialize State
     ↓
Supervisor Agent (update state)
     ↓
Specialized Agent (update state)
     ↓
Service Layer (reads state)
     ↓
Update State with Results
     ↓
Return to Supervisor (or another agent)
     ↓
Final Response
```

## Specialized Agents

### 1. Supervisor Agent

**Role**: Main orchestrator and request router

**Capabilities**:
- Analyze user intent
- Route to appropriate specialized agent
- Maintain conversation context
- Handle multi-turn conversations
- Coordinate complex workflows
- Provide final responses

**Decision Making**:
```
User Input
    ↓
Analyze Intent
    ↓
IF task creation → Planning Agent
IF schedule request → Scheduling Agent
IF "what should I do?" → Suggestion Agent
IF sync issue → Sync Agent
IF general chat → Handle directly
```

**Key Methods**:
- `route_request(state)` - Determine which agent to invoke
- `coordinate_workflow(state)` - Orchestrate multi-agent tasks
- `synthesize_response(state)` - Combine agent outputs

### 2. Planning Agent

**Role**: Task creation, planning, and estimation

**Capabilities**:
- Parse natural language task descriptions
- Extract task details (title, description, deadline)
- Estimate time requirements using LLM + historical data
- Assess energy requirements
- Suggest optimal scheduling
- Handle task dependencies

**Workflow**:
```
START
  │
  ▼
[Extract Task Info from Natural Language]
  │ (Uses LLM)
  ▼
[Estimate Time & Energy Requirements]
  │ (Uses Time Estimation Service + LLM)
  ▼
[Check Calendar Availability]
  │ (Uses Calendar Service)
  ▼
[Suggest Time Blocks]
  │ (Uses LLM + Scheduling Logic)
  ▼
[Consider Context Switching]
  │ (ADHD-specific heuristics)
  ▼
[Create/Update Task]
  │ (Uses Task Service)
  ▼
[Queue for Sync if Enabled]
  │ (Uses Sync Service)
  ▼
END
```

**Example Interaction**:
```
User: "Add task: write report by Friday, probably takes 2 hours"

Planning Agent:
1. Extracts:
   - Title: "Write report"
   - Deadline: Friday (this week)
   - Estimated duration: 2 hours

2. Assesses:
   - Energy: HIGH (creative work)
   - Focus required: Yes
   - Context category: "work"

3. Suggests:
   - Schedule for Thursday morning 9-11am
   - (Peak energy time based on user patterns)

4. Creates task and asks user to confirm
```

### 3. Scheduling Agent

**Role**: Generate optimal schedules

**Capabilities**:
- Create ADHD-friendly schedules
- Balance energy levels throughout day
- Minimize context switching
- Respect user preferences and patterns
- Handle constraints and dependencies
- Propose multiple scheduling options

**Workflow**:
```
START
  │
  ▼
[Get Available Time Slots]
  │ (From Calendar Service)
  ▼
[Analyze Energy Patterns]
  │ (From Energy Service - historical data)
  ▼
[Consider Task Dependencies]
  │ (From Task Service)
  ▼
[Apply ADHD-Friendly Rules]
  │  - Buffer time between tasks (10 min default)
  │  - Avoid excessive context switching
  │  - Match task energy to user energy level
  │  - Respect max focus duration (45 min default)
  ▼
[Generate Schedule Options]
  │ (Uses LLM for optimization)
  ▼
[Rank Options by Suitability]
  │
  ▼
[Present Top 3 Options to User]
  │
  ▼
END
```

**ADHD-Specific Rules**:
1. **Buffer Time**: Add 10-15 min between tasks for recovery
2. **Context Grouping**: Group similar tasks together
3. **Energy Matching**: High-energy tasks during peak times
4. **Break Enforcement**: Mandatory breaks after focus sessions
5. **Flexibility**: Allow easy rescheduling without penalty

### 4. Suggestion Agent

**Role**: Proactive task recommendations

**Capabilities**:
- Analyze current context (time, energy, deadlines)
- Rank tasks by suitability for current moment
- Identify time gaps and suggest fillers
- Remind about approaching deadlines
- Provide reasoning for suggestions

**Workflow**:
```
START
  │
  ▼
[Analyze Current Context]
  │  - Current time of day
  │  - Predicted energy level
  │  - Upcoming calendar events
  │  - Available time before next event
  │  - Incomplete tasks
  ▼
[Rank Tasks by Suitability]
  │ (Uses LLM for complex reasoning)
  │
  │  Factors:
  │  - Energy match (task energy ≈ user energy)
  │  - Duration fit (task fits in available time)
  │  - Priority/urgency
  │  - Context (already in this area/mindset?)
  │  - Deadline proximity
  ▼
[Format Suggestions]
  │  - "Now might be good for X because..."
  │  - "You have 45 min before meeting - try Y"
  │  - "Low energy? Consider these lighter tasks..."
  ▼
[Return Top 3-5 Suggestions with Reasoning]
  │
  ▼
END
```

**Example Output**:
```
"Based on your current context:

1. **Code review for PR #123** (30 min, medium energy)
   → You have 45 minutes before your next meeting
   → Your energy is medium-high right now
   → This is in your current "work" context

2. **Respond to client email** (15 min, low energy)
   → Quick win before lunch
   → Doesn't require deep focus

3. **Plan presentation** (2 hours, high energy)
   → Better to schedule for tomorrow morning (your peak time)
   → Too large for current time slot"
```

### 5. Sync Agent

**Role**: Manage bidirectional sync with Apple

**Capabilities**:
- Queue and execute sync operations
- Handle Apple Reminders sync
- Handle Apple Calendar sync
- Detect and resolve conflicts
- Track sync status and errors
- Retry failed syncs

**Workflow**:
```
START
  │
  ▼
[Check Pending Operations]
  │
  ├──► [Local → Apple] Path
  │      │
  │      ├─► Create Reminder/Event in Apple
  │      ├─► Update existing Reminder/Event
  │      └─► Delete Reminder/Event
  │
  └──► [Apple → Local] Path
         │
         ├─► Detect Changes in Apple
         ├─► Compare timestamps
         ├─► Resolve Conflicts (if any)
         │     - Last-write-wins
         │     - Or user prompt for important conflicts
         └─► Update Local Database
  │
  ▼
[Update Sync Metadata]
  │  - last_synced_at timestamp
  │  - sync_status
  ▼
[Report Status]
  │
  ▼
END
```

**Conflict Resolution**:
```
IF local_timestamp > apple_timestamp:
    Local change is newer → Push to Apple
ELIF apple_timestamp > local_timestamp:
    Apple change is newer → Pull to Local
ELSE IF timestamps equal but content differs:
    Apply conflict resolution strategy:
    - Default: Last-write-wins (based on modified_at)
    - Optional: Ask user to choose
```

### 6. Energy Tracking Agent

**Role**: Learn and predict energy patterns

**Capabilities**:
- Collect energy data points
- Analyze temporal patterns
- Predict current energy level
- Suggest optimal times for different tasks
- Identify energy trends

**Workflow**:
```
START
  │
  ▼
[Collect Data Points]
  │  - Task completions (when? how long?)
  │  - Self-reported energy (from user)
  │  - Time of day
  │  - Context switches
  │  - Break patterns
  ▼
[Analyze Patterns]
  │ (Optional: Use LLM for complex pattern recognition)
  │
  │  Looking for:
  │  - Consistent high-energy times (e.g., 9am-12pm)
  │  - Consistent low-energy times (e.g., 2pm-4pm)
  │  - Day-of-week patterns (Monday vs Friday)
  │  - Post-break energy boosts
  ▼
[Update Energy Profile]
  │  - Store in UserPreferences
  │  - Maintain historical accuracy metrics
  ▼
[Predict Current Energy]
  │  - Based on time of day
  │  - Based on recent activity
  │  - Based on historical patterns
  ▼
[Store in AgentState]
  │
  ▼
END
```

**Energy Prediction**:
```python
def predict_energy(current_time, recent_tasks, user_patterns):
    # Base prediction from historical patterns
    base_energy = lookup_pattern(current_time, user_patterns)

    # Adjust for recent activity
    if context_switches_recently > 3:
        base_energy -= 1  # Reduced by switching

    if time_since_break > max_focus_duration:
        base_energy -= 1  # Fatigue setting in

    if just_completed_high_energy_task:
        base_energy -= 1  # Post-task depletion

    return clamp(base_energy, LOW, HIGH)
```

## Agent Workflows

### Multi-Agent Collaboration Example

**Scenario**: User says "Plan my day"

```
1. [Supervisor] Receives request
      ↓
   Routes to Scheduling Agent
      ↓
2. [Scheduling Agent] Needs information
      ↓
   Calls Task Service → Get incomplete tasks
   Calls Calendar Service → Get events
   Calls Energy Service → Get patterns
      ↓
3. [Energy Agent] Provides prediction
      ↓
   "User typically high energy 9am-12pm"
   "Low energy 2pm-4pm"
   "Medium energy evening"
      ↓
4. [Scheduling Agent] Generates options
      ↓
   Uses LLM to create 3 schedule options
   Applies ADHD rules (buffers, energy matching)
      ↓
5. [Supervisor] Presents options to user
      ↓
   User selects Option 2
      ↓
6. [Scheduling Agent] Creates schedule
      ↓
   Creates TimeBlocks via Calendar Service
   Updates Tasks via Task Service
      ↓
7. [Sync Agent] (If sync enabled) Syncs to Apple
      ↓
8. [Supervisor] Confirms completion
      ↓
   "Your day is planned! I've created X time blocks..."
```

## LangGraph Implementation

### Graph Structure

```python
from langgraph.graph import StateGraph, END

# Create graph builder
graph_builder = StateGraph(AgentState)

# Add agent nodes
graph_builder.add_node("supervisor", supervisor_node)
graph_builder.add_node("planning_agent", planning_agent_node)
graph_builder.add_node("scheduling_agent", scheduling_agent_node)
graph_builder.add_node("suggestion_agent", suggestion_agent_node)
graph_builder.add_node("sync_agent", sync_agent_node)
graph_builder.add_node("energy_agent", energy_agent_node)

# Define routing from supervisor
graph_builder.add_conditional_edges(
    "supervisor",
    route_to_agent,  # Routing function
    {
        "planning": "planning_agent",
        "scheduling": "scheduling_agent",
        "suggestion": "suggestion_agent",
        "sync": "sync_agent",
        "energy": "energy_agent",
        "end": END
    }
)

# All agents return to supervisor
for agent in ["planning_agent", "scheduling_agent", "suggestion_agent",
              "sync_agent", "energy_agent"]:
    graph_builder.add_edge(agent, "supervisor")

# Set entry point
graph_builder.set_entry_point("supervisor")

# Compile graph
graph = graph_builder.compile()
```

### Routing Logic

```python
def route_to_agent(state: AgentState) -> str:
    """Determine which agent should handle the request"""

    user_input = state["user_input"].lower()

    # Intent classification (can use LLM for complex cases)
    if any(word in user_input for word in ["add", "create", "new task"]):
        return "planning"

    elif any(word in user_input for word in ["plan my day", "schedule", "organize"]):
        return "scheduling"

    elif any(word in user_input for word in ["what should i", "suggest", "recommend"]):
        return "suggestion"

    elif any(word in user_input for word in ["sync", "apple", "calendar"]):
        return "sync"

    elif state["needs_clarification"]:
        return "end"  # Return to user for clarification

    else:
        # Use LLM to classify intent
        intent = classify_intent_with_llm(user_input)
        return intent
```

### Agent Node Implementation

```python
async def planning_agent_node(state: AgentState) -> AgentState:
    """Planning agent node function"""

    # Extract task details using LLM
    task_details = await extract_task_details(
        state["user_input"],
        state["messages"]
    )

    # Estimate duration
    estimated_duration = await estimate_duration(
        task_details,
        historical_data=get_similar_tasks(task_details)
    )

    # Assess energy requirements
    energy_level = assess_energy_requirements(task_details)

    # Check calendar availability
    availability = check_availability(
        estimated_duration,
        state["calendar_events"]
    )

    # Create task
    task = create_task(
        title=task_details["title"],
        description=task_details.get("description"),
        estimated_duration_minutes=estimated_duration,
        estimated_energy_level=energy_level
    )

    # Update state
    state["current_task"] = task
    state["agent_response"] = format_task_confirmation(task, availability)
    state["active_agent"] = "planning_agent"

    return state
```

## Agent Coordination

### Sequential Workflows

Some operations require sequential agent execution:

```
User: "Add 'write report' and schedule it"
  ↓
[Supervisor]
  ↓
[Planning Agent] Creates task
  ↓
[Supervisor] (with created task in state)
  ↓
[Scheduling Agent] Schedules the task
  ↓
[Supervisor] Returns combined response
```

### Parallel Workflows

Some operations can happen in parallel (future enhancement):

```
User: "Sync all my tasks"
  ↓
[Supervisor]
  ↓
[Sync Agent] ─┬─► Sync Reminders
              ├─► Sync Calendar
              └─► Update metadata
  ↓
[Supervisor] Returns combined status
```

### Error Handling

```
[Agent Node]
  ↓
Try:
    Execute agent logic
    Update state
Except LLMError:
    Retry with simplified prompt
    Or fallback to rules-based logic
Except ValidationError:
    Set needs_clarification = True
    Return to supervisor for user input
Except Exception:
    Log error
    Return graceful error message
    Suggest manual action
```

## Extension: Adding New Agents

### Steps to Add a New Agent

1. **Define Agent Class**
```python
class HabitTrackingAgent(BaseAgent):
    def execute(self, state: AgentState) -> AgentState:
        # Agent logic
        pass

    def should_handle(self, state: AgentState) -> bool:
        # Return True if this agent should handle request
        pass
```

2. **Create Node Function**
```python
async def habit_tracking_agent_node(state: AgentState) -> AgentState:
    agent = HabitTrackingAgent(llm_service)
    return await agent.execute(state)
```

3. **Add to Graph**
```python
graph_builder.add_node("habit_agent", habit_tracking_agent_node)
graph_builder.add_edge("habit_agent", "supervisor")
```

4. **Update Routing**
```python
def route_to_agent(state: AgentState) -> str:
    # ... existing logic ...

    if "habit" in user_input or "routine" in user_input:
        return "habit_agent"
```

## Related Documentation

- [System Overview](system-overview.md)
- [Data Models](data-models.md)
- [LLM Integration](integration-design.md#llm-provider-abstraction)
- [Extension Guide](../technical/extension-guide.md)
