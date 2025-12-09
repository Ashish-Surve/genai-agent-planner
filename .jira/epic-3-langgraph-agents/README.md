# Epic 3: LangGraph Agents

## Overview

This epic implements the core AI agent system using LangGraph for orchestration. The system uses a **supervisor pattern** where a main supervisor agent routes requests to specialized agents that handle specific tasks.

## Epic Goals

1. Build the LangGraph state management foundation
2. Implement specialized AI agents for different tasks
3. Create supervisor for routing and coordination
4. Integrate all agents into a cohesive workflow
5. Enable multi-turn conversations with context awareness

## Stories in This Epic

### ✅ ADHD-11: LangGraph State & Base Agent
**Time**: 3h | **Status**: 📋 Not Started

Create the foundation for the agent system:
- `AgentState` TypedDict definition
- `StateManager` utility class
- `BaseAgent` abstract class
- State management helpers

**Why it matters**: This is the foundation that all agents build upon. Proper state management is critical for multi-agent coordination.

---

### ✅ ADHD-12: Supervisor Agent
**Time**: 3h | **Status**: 📋 Not Started

Implement the main orchestrator:
- Intent classification
- Request routing to specialists
- Multi-agent coordination
- Response synthesis

**Why it matters**: The supervisor is the "brain" that decides which specialist agent should handle each request.

---

### ✅ ADHD-13: Planning Agent
**Time**: 3h | **Status**: 📋 Not Started

Build the task creation specialist:
- Natural language task extraction
- Time and energy estimation with LLM
- Calendar availability checking
- Scheduling suggestions

**Why it matters**: This agent makes task creation effortless by understanding natural language and providing intelligent defaults.

---

### ✅ ADHD-14: Scheduling Agent
**Time**: 4h | **Status**: 📋 Not Started

Create the schedule generation specialist:
- ADHD-friendly schedule generation
- Energy level matching
- Buffer time and context switching
- Multiple schedule options

**Why it matters**: This is the core ADHD-specific intelligence that creates optimized, sustainable schedules.

---

### ✅ ADHD-15: Suggestion Agent
**Time**: 2h | **Status**: 📋 Not Started

Implement the recommendation specialist:
- Context analysis (time, energy, availability)
- Task ranking by suitability
- Proactive suggestions with reasoning
- Decision paralysis reduction

**Why it matters**: Helps ADHD users overcome "what should I do next?" paralysis with clear, contextual recommendations.

---

### ✅ ADHD-16: Graph Builder & Integration
**Time**: 3h | **Status**: 📋 Not Started

Tie everything together:
- Graph builder and compilation
- Node functions for all agents
- Edge routing logic
- Error handling and recovery
- Integration testing

**Why it matters**: This is the "glue" that makes all agents work together seamlessly.

---

## Total Epic Estimate

**~18 hours** across **5 sessions** (3-4 hours per session)

## Architecture Pattern

This epic implements the **Supervisor Pattern**:

```
User Input
    ↓
[Supervisor Agent]
    ↓
    ├─→ [Planning Agent] ──→ Create/estimate tasks
    ├─→ [Scheduling Agent] ─→ Generate schedules
    └─→ [Suggestion Agent] ─→ Recommend tasks
    ↓
Response to User
```

### Why Supervisor Pattern?

1. **Separation of Concerns**: Each agent has a focused responsibility
2. **Flexibility**: Easy to add new agents without modifying existing ones
3. **Scalability**: Agents can be distributed if needed
4. **Error Handling**: Centralized failure management
5. **Context Management**: Single point for conversation state

## Dependencies

### Prerequisites (Must be complete before starting)
- ✅ ADHD-1 through ADHD-5: Foundation (database, repositories)
- ✅ ADHD-6: Configuration & Logging
- ✅ ADHD-7: LLM Service & Provider Factory
- ✅ ADHD-8: Task Service
- ✅ ADHD-9: Calendar Service
- ✅ ADHD-10: Time Estimation Service

### Story Dependencies Within Epic
```
ADHD-11 (State & Base)
    ↓
ADHD-12 (Supervisor) ← Required by all specialists
    ↓
ADHD-13 (Planning) ─┐
ADHD-14 (Scheduling) ├─→ ADHD-16 (Graph Builder)
ADHD-15 (Suggestion) ┘
```

**Important**: You can work on ADHD-13, 14, and 15 in parallel after ADHD-12 is complete!

## Implementation Strategy

### Session 1: Foundation (ADHD-11)
Build the state management and base agent foundation. This is critical infrastructure.

### Session 2: Supervisor (ADHD-12)
Implement the supervisor agent. Test routing logic thoroughly.

### Session 3: Specialist Agents (ADHD-13 + ADHD-15)
Implement Planning and Suggestion agents in one session (5 hours total, fits in a long session).

### Session 4: Scheduling Agent (ADHD-14)
Implement the most complex agent. Take your time with the ADHD-specific rules.

### Session 5: Integration (ADHD-16)
Bring it all together. Test the complete workflow end-to-end.

## Testing Strategy

### Unit Tests
Each agent has comprehensive unit tests:
- Agent initialization
- Execution logic
- Service integration
- Error handling
- Mock LLM responses

### Integration Tests
Test the complete workflow:
- Graph construction
- Routing logic
- State persistence
- Error recovery
- Multi-agent coordination

## Key Features Delivered

After completing this epic, you'll have:

1. **Multi-Agent System**: Coordinated specialists working together
2. **Intelligent Routing**: Automatic request classification and routing
3. **Task Creation**: Natural language task extraction
4. **Schedule Generation**: ADHD-friendly schedule optimization
5. **Proactive Suggestions**: Context-aware task recommendations
6. **Error Handling**: Graceful error recovery
7. **Conversation Context**: Multi-turn conversations with state

## Quality Standards

All code in this epic must meet:

### Readability
- Clear variable and function names
- Type hints on all functions
- Comprehensive docstrings
- Comments explaining WHY, not WHAT

### Debuggability
- Logging at INFO and DEBUG levels
- Clear error messages with context
- State inspection capabilities
- Graph visualization

### Maintainability
- Single Responsibility Principle
- DRY (Don't Repeat Yourself)
- Consistent patterns across agents
- Small, focused functions

### Testing
- Unit tests for all agents
- Integration tests for workflows
- Mock LLM for fast testing
- Edge cases covered

## Common Pitfalls

### ❌ Don't Do This:
- Skip state management utilities (you'll regret it!)
- Hardcode routing logic in multiple places
- Forget to test error scenarios
- Mix agent responsibilities
- Skip logging statements

### ✅ Do This Instead:
- Use StateManager for all state operations
- Centralize routing in supervisor
- Test error handling thoroughly
- Keep agents focused on one task
- Log every major decision

## Files Created in This Epic

```
src/adhd_planner/
├── agents/
│   ├── __init__.py              # Agent exports
│   ├── base.py                  # Base agent class
│   ├── supervisor.py            # Supervisor agent
│   ├── planning_agent.py        # Planning agent
│   ├── scheduling_agent.py      # Scheduling agent
│   └── suggestion_agent.py      # Suggestion agent
│
├── graph/
│   ├── __init__.py              # Graph exports
│   ├── state.py                 # State definition
│   ├── state_utils.py           # State utilities
│   ├── builder.py               # Graph builder
│   └── nodes.py                 # Node functions
│
└── utils/prompts/
    ├── supervisor_prompts.py    # Supervisor prompts
    ├── planning_prompts.py      # Planning prompts
    ├── scheduling_prompts.py    # Scheduling prompts
    └── suggestion_prompts.py    # Suggestion prompts

tests/
├── unit/
│   ├── test_base_agent.py
│   ├── test_supervisor.py
│   ├── test_planning_agent.py
│   ├── test_scheduling_agent.py
│   └── test_suggestion_agent.py
│
└── integration/
    └── test_graph_workflow.py   # End-to-end tests

scripts/
└── visualize_graph.py           # Graph visualization
```

## Next Epic

After completing Epic 3, you'll move to:

**Epic 4: Streamlit UI (Stories 17-21)**
- Build the user interface
- Integrate with agent system
- Create interactive components
- Enable visual time blocking

## Success Metrics

You'll know this epic is complete when:

- [ ] All 6 story cards implemented
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Graph compiles successfully
- [ ] Can execute complete workflows
- [ ] Error handling works
- [ ] State persists correctly
- [ ] Graph visualization displays
- [ ] Code reviewed and documented

## Resources

### LangGraph Documentation
- [LangGraph Basics](https://langchain-ai.github.io/langgraph/)
- [State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)

### Project Documentation
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System architecture
- [Agent System Design](../../docs/architecture/agent-system.md)
- [Data Models](../../docs/architecture/data-models.md)

### Code Examples
- See each story card for detailed implementation examples
- Check tests for usage patterns
- Review prompts for LLM interaction examples

## Tips for Success

1. **Start with ADHD-11**: Don't skip the foundation!
2. **Test as you go**: Don't wait until the end
3. **Use mock LLM**: Fast iteration during development
4. **Log everything**: You'll thank yourself later
5. **Keep agents focused**: Resist scope creep
6. **Read the prompts**: They guide agent behavior
7. **Visualize the graph**: Helps understand flow
8. **Take breaks**: 18 hours is a lot!

## Questions?

If you get stuck:
1. Review the story card's implementation notes
2. Check the architecture documentation
3. Look at test files for examples
4. Run the visualization script
5. Ask Claude to explain a concept

## Let's Build This! 🚀

The agent system is the heart of ADHD Planner. Take your time, test thoroughly, and create something amazing.

Remember: **Progress over perfection!**

Good luck! 💪
