# ADHD-XX: Improve Agent Architecture for Conversational Chat Interface

## Issue Type
Enhancement / Architecture Improvement

## Priority
High

## Summary
The current agent architecture uses a one-shot routing pattern where the Supervisor routes to a specialist agent and then immediately ends the flow. This design loses conversation context between messages, making it unsuitable for a multi-turn chat interface.

---

## Problem Statement

### Current Behavior
1. Each user message creates a **fresh state** - no memory of previous turns
2. Specialist agents route directly to `END` - no follow-up or clarification possible
3. No LangGraph memory/checkpointing - context dies after each response
4. Multi-step workflows are impossible (e.g., "add task" → "what's the deadline?" → "schedule it")

### Current Flow (Broken for Chat)
```
User Message → Supervisor → Specialist Agent → END (context lost)
User Message → Supervisor → Specialist Agent → END (starts fresh)
```

### Expected Behavior
```
User: "Add a task: write report"
  → Planning Agent: "What's the deadline?"
User: "Friday"
  → Planning Agent (remembers task): "Created! Want me to schedule it?"
User: "Yes, tomorrow morning"
  → Scheduling Agent (uses task from context): "Scheduled for 9-11am"
```

---

## Root Cause Analysis

### 1. Stateless Execution
**File:** `src/adhd_planner/core/chat_handler.py:52-62`
```python
def _run_graph(self, user_input: str, context: dict) -> str:
    # Creates fresh state every time - no memory
    state = StateManager.create_initial_state(user_input)
    state["context"] = context
    result = self.graph.invoke(state)
```

### 2. One-Shot Graph Edges
**File:** `src/adhd_planner/graph/builder.py:86-89`
```python
# Agents go straight to END - no follow-up possible
self.graph.add_edge("planning_agent", END)
self.graph.add_edge("scheduling_agent", END)
self.graph.add_edge("suggestion_agent", END)
```

### 3. No Memory Checkpointer
The graph is compiled without a checkpointer:
```python
self.compiled_graph = self.graph.compile()  # No memory!
```

---

## Proposed Solution

### Architecture: Cyclic Graph with Memory Checkpointing

```
                    ┌─────────────────────┐
                    │      Supervisor     │◄────────────────────┐
                    └──────────┬──────────┘                     │
                               │                                │
              ┌────────────────┼────────────────┐               │
              ▼                ▼                ▼               │
        ┌──────────┐    ┌──────────┐    ┌──────────┐           │
        │ Planning │    │Scheduling│    │Suggestion│           │
        │  Agent   │    │  Agent   │    │  Agent   │           │
        └────┬─────┘    └────┬─────┘    └────┬─────┘           │
             │               │               │                  │
             └───────────────┴───────────────┘                  │
                             │                                  │
                    ┌────────▼────────┐                         │
                    │  Response Node  │─────────────────────────┘
                    │ (decides: END   │        (if needs_followup)
                    │  or continue)   │
                    └────────┬────────┘
                             │ (if complete)
                            END
```

### Key Changes

#### 1. Add Memory Checkpointer
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
self.compiled_graph = self.graph.compile(checkpointer=memory)
```

#### 2. Use Thread IDs for Conversation Sessions
```python
# In ChatHandler
config = {"configurable": {"thread_id": self.session_id}}
result = self.graph.invoke(state, config)
```

#### 3. Create Cyclic Graph (Specialists → Supervisor)
```python
# Replace direct END edges with conditional routing
self.graph.add_conditional_edges(
    "response_node",
    should_continue,
    {
        "continue": "supervisor",
        "end": END
    }
)
```

#### 4. Add Response Node
New node that decides if conversation should continue:
- Check if agent needs clarification (`needs_clarification` flag)
- Check if workflow is complete
- Check if user confirmation is needed

#### 5. Update AgentState for Multi-Turn
```python
class AgentState(TypedDict):
    # ... existing fields ...

    # New fields for multi-turn support
    needs_followup: bool              # Agent needs more info
    pending_action: dict | None       # Action awaiting confirmation
    conversation_stage: str           # "initial", "clarifying", "confirming", "complete"
    workflow_context: dict            # Accumulated context across turns
```

---

## Implementation Plan

### Phase 1: Add Memory Checkpointing
- [ ] Add `MemorySaver` to `GraphBuilder`
- [ ] Pass `thread_id` config through `ChatHandler`
- [ ] Store `thread_id` in Streamlit session state
- [ ] Add "New Conversation" button to reset thread

### Phase 2: Create Cyclic Graph Structure
- [ ] Create `ResponseNode` class
- [ ] Add `should_continue()` routing function
- [ ] Update graph edges: specialists → response_node → supervisor/END
- [ ] Update `AgentState` with multi-turn fields

### Phase 3: Update Agents for Multi-Turn
- [ ] Add `needs_followup` flag handling to each agent
- [ ] Implement `pending_action` for confirmations
- [ ] Update Supervisor to handle follow-up context
- [ ] Add conversation stage tracking

### Phase 4: Update Chat Interface
- [ ] Handle streaming responses properly
- [ ] Show "waiting for input" states
- [ ] Add conversation reset functionality
- [ ] Display pending actions/confirmations clearly

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/adhd_planner/graph/builder.py` | Add MemorySaver, cyclic edges |
| `src/adhd_planner/graph/state.py` | Add multi-turn state fields |
| `src/adhd_planner/graph/nodes.py` | Add ResponseNode |
| `src/adhd_planner/graph/edges.py` | Add `should_continue()` function |
| `src/adhd_planner/core/chat_handler.py` | Add thread_id support |
| `src/adhd_planner/core/session_manager.py` | Store thread_id per session |
| `src/adhd_planner/agents/supervisor.py` | Handle follow-up routing |
| `src/adhd_planner/agents/planning_agent.py` | Add clarification flow |
| `src/adhd_planner/agents/scheduling_agent.py` | Add clarification flow |
| `src/adhd_planner/agents/suggestion_agent.py` | Add clarification flow |
| `src/adhd_planner/ui/pages/1_Chat.py` | Add new conversation button |

---

## Acceptance Criteria

- [ ] Conversation context persists across multiple messages
- [ ] Agents can ask clarifying questions and receive answers
- [ ] Multi-step workflows work (add task → set deadline → schedule)
- [ ] "New Conversation" button resets context
- [ ] Previous conversation can be resumed (same thread_id)
- [ ] No regression in single-turn interactions
- [ ] Unit tests for multi-turn flows

---

## Testing Scenarios

### Scenario 1: Task Creation with Follow-up
```
User: "Add a task"
Bot: "What would you like to call this task?"
User: "Write quarterly report"
Bot: "Got it! How long do you think it will take?"
User: "About 3 hours"
Bot: "Created 'Write quarterly report' (3 hours). Would you like me to schedule it?"
```

### Scenario 2: Context Preservation
```
User: "I need to prepare for the meeting"
Bot: "I'll create a task for meeting preparation. When is the meeting?"
User: "Thursday at 2pm"
Bot: "Created 'Prepare for meeting' due Thursday 2pm. I suggest scheduling prep time Wednesday afternoon during your high-energy window."
```

### Scenario 3: Agent Handoff with Context
```
User: "Add task: review PR, takes 30 minutes"
Bot: "Created 'Review PR' (30 min). Want me to schedule it?"
User: "Yes, find time today"
Bot: [Scheduling agent uses task from Planning agent] "Scheduled for 3:30-4:00 PM today."
```

---

## Dependencies

- LangGraph >= 0.2.0 (for MemorySaver)
- No new external dependencies required

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Memory usage growth | High | Implement conversation TTL, limit history length |
| Circular routing loops | Medium | Add max iteration limit, loop detection |
| Breaking existing flows | High | Comprehensive test coverage, feature flag |
| Increased latency | Low | Optimize state serialization |

---

## References

- [LangGraph Memory Documentation](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph Multi-Agent Tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- Current architecture doc: `docs/architecture/agent-system.md`

---

## Labels
`enhancement`, `architecture`, `agent-system`, `priority-high`

## Story Points
8

## Epic
Agent System Improvements
