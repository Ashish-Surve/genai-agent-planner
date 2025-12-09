# Epic 4: Streamlit UI

## Overview

This epic implements the Streamlit-based user interface for ADHD Planner. It provides a web-based UI with four main pages: Chat, Tasks, Calendar, and Settings.

**Total Estimated Time**: ~14 hours (4 sessions)

## Stories

| Story | Title | Time | Status |
|-------|-------|------|--------|
| ADHD-17 | Streamlit App Structure | 2h | 📋 Not Started |
| ADHD-18 | Chat Page & Components | 3h | 📋 Not Started |
| ADHD-19 | Tasks Page & Components | 3h | 📋 Not Started |
| ADHD-20 | Calendar View | 4h | 📋 Not Started |
| ADHD-21 | Settings Page | 2h | 📋 Not Started |

## Prerequisites

Before starting Epic 4, ensure these are complete:
- ✅ Epic 3: LangGraph Agents (ADHD-11 to ADHD-16)
- ✅ ADHD-8: Task Service
- ✅ ADHD-9: Calendar Service
- ✅ ADHD-6: Configuration & Logging

## Implementation Order

Stories must be completed in sequence:

```
ADHD-17 (App Structure)
    ↓
ADHD-18 (Chat Page) ─────┐
    ↓                    │
ADHD-19 (Tasks Page) ────┤ (can work in parallel after 17)
    ↓                    │
ADHD-20 (Calendar View) ─┘
    ↓
ADHD-21 (Settings Page)
```

## Key Components

### Pages
- **Chat**: Conversational interface with AI assistant
- **Tasks**: Task list with filtering and quick actions
- **Calendar**: Day view with time blocks
- **Settings**: User preferences configuration

### Core Components
- **SessionManager**: Streamlit session state management
- **SettingsManager**: User preferences persistence
- **ChatHandler**: Agent system integration

### UI Components
- `chat_message.py` - Message display
- `task_card.py` - Task list items
- `time_block.py` - Calendar time blocks
- `day_timeline.py` - Daily schedule view

## MVP Principles

This epic follows MVP principles:
- **Simple, functional UI** - No fancy animations or complex interactions
- **Mock data fallbacks** - UI works without backend services
- **Basic components** - No drag-and-drop, inline editing, or advanced features
- **Streamlit native** - Use built-in components where possible

## Running the UI

```bash
# From project root
uv run streamlit run src/adhd_planner/ui/app.py

# Access at http://localhost:8501
```

## File Structure

```
src/adhd_planner/
├── ui/
│   ├── app.py                    # Main entry point
│   ├── pages/
│   │   ├── 1_💬_Chat.py
│   │   ├── 2_📋_Tasks.py
│   │   ├── 3_📅_Calendar.py
│   │   └── 4_⚙️_Settings.py
│   ├── components/
│   │   ├── chat_message.py
│   │   ├── chat_input.py
│   │   ├── task_card.py
│   │   ├── time_block.py
│   │   └── day_timeline.py
│   └── styles/
│       └── (CSS files if needed)
└── core/
    ├── session_manager.py
    ├── settings_manager.py
    └── chat_handler.py
```

## Testing

Each story includes unit tests. Run all Epic 4 tests:

```bash
uv run pytest tests/unit/test_session_manager.py tests/unit/test_chat_handler.py tests/unit/test_tasks_page.py tests/unit/test_calendar_view.py tests/unit/test_settings_manager.py -v
```

## What This Epic Does NOT Include

- User authentication/login
- Multi-user support
- Mobile-responsive design
- Drag-and-drop interactions
- Real-time updates/websockets
- Offline support
- Advanced theming

These are deferred to future iterations.

## After Completing Epic 4

Proceed to **Epic 5: Apple Integration** (ADHD-22 to ADHD-25)
