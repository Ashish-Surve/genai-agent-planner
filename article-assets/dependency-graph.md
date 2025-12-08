# ADHD-Planner: Story Dependency Graph

This graph shows the prerequisite relationships between stories, ensuring proper implementation order.

```
ADHD-1 (Setup)
    ↓
ADHD-2 (Database) → ADHD-3 (Models) → ADHD-4 (Base Repo) → ADHD-5 (Task Repo)
                                                                    ↓
ADHD-6 (Config) → ADHD-7 (LLM Service) ────────────────────────────┤
                      ↓                                             ↓
                  ADHD-8 (Task Service) → ADHD-9 (Calendar Service)
                      ↓                           ↓
                  ADHD-10 (Time Est) ─────────────┤
                      ↓                           ↓
                  ADHD-11 (LangGraph State) ──────┤
                      ↓
            ADHD-12 (Supervisor) → ADHD-13 (Planning) → ADHD-14 (Scheduling)
                      ↓                                          ↓
            ADHD-15 (Suggestion) ──────────────────────────────┤
                      ↓                                          ↓
            ADHD-16 (Graph Builder) ───────────────────────────┤
                      ↓
            ADHD-17 (UI Structure) → ADHD-18 (Chat) → ADHD-19 (Tasks)
                      ↓                                      ↓
            ADHD-20 (Calendar View) → ADHD-21 (Settings) ──┤
                      ↓
            ADHD-22 (Apple Perms) → ADHD-23 (Reminders) → ADHD-24 (Calendar)
                      ↓                                          ↓
            ADHD-25 (Sync Service) ────────────────────────────┤
                      ↓
            ADHD-26 (Energy Service) → ADHD-27 (Energy Agent)
                      ↓                          ↓
            ADHD-28 (Sync Agent) → ADHD-29 (Buffer/Context)
                      ↓
            ADHD-30 (Error Handling) → ADHD-31 (Unit Tests)
                      ↓                          ↓
            ADHD-32 (Integration Tests) → ADHD-33 (Polish)
```

## Critical Path Analysis

**Foundation Phase** (Must complete sequentially):
- ADHD-1 → ADHD-2 → ADHD-3 → ADHD-4 → ADHD-5

**Service Phase** (Can parallelize after repositories):
- ADHD-6, ADHD-7 (independent)
- ADHD-8, ADHD-9, ADHD-10 (require repos)

**Agent Phase** (Sequential within epic):
- ADHD-11 (base) → ADHD-12 (supervisor) → ADHD-13, 14, 15 (specialists) → ADHD-16 (integration)

**UI Phase** (Requires agents):
- ADHD-17 (base) → ADHD-18, 19, 20, 21 (pages)

**Integration Phase** (Requires core system):
- ADHD-22 → ADHD-23, ADHD-24 → ADHD-25

**Enhancement Phase** (Requires integrations):
- ADHD-26 → ADHD-27, ADHD-28 → ADHD-29

**Quality Phase** (End-to-end):
- ADHD-30 → ADHD-31, ADHD-32 → ADHD-33

## Dependency Rules

1. **No story can start without prerequisites complete**
2. **Foundation must finish before services**
3. **Services must finish before agents**
4. **Agents must finish before UI**
5. **Core system must work before Apple integration**
6. **All features must work before polish/testing**

This strict dependency enforcement prevents context thrashing and ensures stable foundations.
