# Vibe Coding: Can One Data Scientist Do the Work of a Whole Dev Team?

## The Question

Can a single data scientist with AI assistance match the output of an entire development team? I decided to find out by building ADHD-Planner—a production-ready multi-agent task management system—using Claude and a methodology I'm calling "vibe coding."

## What is Vibe Coding?

Vibe coding is about letting AI handle the implementation while you focus on architecture and design. You don't micromanage the code—you trust the system and let it flow. But that only works if you have an excellent blueprint first.

The constraint: I work in 4-hour Claude sessions. No context persistence between sessions. That means everything—the entire system design—had to be documented upfront.

## Building the Architecture First

Before writing a single line of code, I spent time on architecture. I created:

- **ARCHITECTURE.md** (650+ lines): A 5-layer system design
- **.jira folder**: 33 story cards with complete implementation guides
- **Epic breakdown**: 7 epics, 89 hours of work, broken into 2-4 hour chunks

The 5-layer architecture:

```
Presentation Layer (Streamlit UI)
    ↓
Application Layer (LangGraph Agents)
    ↓
Service Layer (Business Logic)
    ↓
Data Access Layer (Repositories)
    ↓
Persistence Layer (SQLite, Apple APIs)
```

Each layer has clear responsibilities. No ambiguity.

## The System Design

**LangGraph Agents**: A supervisor agent routes requests to specialists:
- Planning Agent: Creates tasks
- Scheduling Agent: Generates schedules
- Suggestion Agent: Recommends tasks
- Sync Agent: Handles Apple Reminders/Calendar sync
- Energy Tracker: Monitors ADHD-specific energy patterns

**Services**: Task Service, Calendar Service, LLM Service, Sync Service, Energy Service, Time Estimation Service.

**Data**: SQLAlchemy models, Pydantic validation, SQLite storage.

**Flexibility**: Supports multiple LLM providers (Ollama, Gemini, Claude).

## How Story Cards Work

Each story card is a complete specification:

```
ADHD-3: Pydantic Models & Enums

Time: 2 hours
Files to create: 9 files
Prerequisites: ADHD-2

[Complete code examples for each step]
[12 test cases with expected outputs]
[Common issues and solutions]
```

No back-and-forth. No clarifications needed. Claude reads the story, implements it, tests it, done.

## The Progress So Far

- **3 stories complete**: Setup, Database, Pydantic Models (7 hours)
- **30 stories remaining**: ~82 hours
- **Timeline**: 8-12 weeks at 2-3 sessions per week
- **Team estimate**: 3-4 months with 3-4 developers

## Why This Works

1. **Documentation = Executable Spec**: The architecture IS the implementation guide
2. **No Context Loss**: All state lives in docs, not AI memory
3. **Consistent Patterns**: Story cards enforce Repository, Factory, Strategy patterns
4. **Built-in Testing**: Every story includes a test suite
5. **Dependency Tracking**: Strict order prevents broken dependencies

## The Trade-offs

**What AI does well:**
- Implementing well-defined specs
- Following patterns consistently
- Writing boilerplate with variations
- Generating comprehensive tests
- Creating documentation

**What AI struggles with:**
- High-level architecture (still human-led)
- Ambiguous requirements
- Creative problem-solving without constraints
- Understanding implicit business logic

## The Answer: 3-4x, Not 10x

Am I doing the work of 4 developers? Not quite.

But I'm moving **3-4x faster** than I would alone, with **zero context coordination overhead**. I'm not waiting for code reviews, merge conflicts, or team sync meetings.

The productivity gain isn't from AI coding faster—it's from:
- Eliminating coordination overhead
- Perfect consistency in patterns
- Built-in quality from the start
- No time lost explaining context

## Key Lessons

**Do this:**
- ✅ Design comprehensively before coding
- ✅ Break work into <4 hour chunks
- ✅ Include complete code examples in specs
- ✅ Build dependency graphs upfront
- ✅ Test as you go, not at the end

**Don't do this:**
- ❌ Start coding without architecture
- ❌ Expect AI to remember things between sessions
- ❌ Skip testing until the end
- ❌ Treat AI as a pair programmer (it's an implementation engine)

## The New Developer Paradigm

The 10x developer doesn't code 10x faster. They architect 10x smarter and leverage tools 10x better.

With AI assistance, solo developers can now build systems that previously required teams. Not because AI is magic—but because good documentation is force multiplier.

ADHD-Planner is a working example of this. It's real. It's production-ready. It's built one AI session at a time.

The future isn't AI replacing developers. It's developers amplifying their output through disciplined design and AI implementation.

## What's Next

I'm working through the stories one session at a time. Next up: Base Repository Pattern (ADHD-4). Then services, then agents, then UI, then Apple integration.

You can follow the progress in the [GitHub repo](https://github.com/Ashish-Surve/genai-agent-planner/tree/dev).

The bet: 89 hours of solo work + AI assistance beats the traditional estimate of 3-4 months with a team.

Time will tell.

---

**Vibe coding**: Trust the system, follow the plan, let AI implement. It's not magic—it's architecture.
