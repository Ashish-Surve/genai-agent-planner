# ADHD Planner

An AI-powered planning assistant designed specifically for people with ADHD, featuring intelligent task management, energy-aware scheduling, and seamless integration with Apple's ecosystem.

## Overview

ADHD Planner is a local-first, agent-based planning tool that helps you manage tasks, plan your day, and maintain productivity while accounting for the unique challenges of ADHD. It uses LangGraph-powered AI agents to provide intelligent scheduling suggestions, track your energy patterns, and minimize context switching.

## Key Features

### Core Capabilities
- **Conversational Task Management**: Create and manage tasks through natural language chat
- **Intelligent Scheduling**: AI-powered schedule generation that considers your energy levels and work patterns
- **Energy Tracking**: Learn and predict your peak productivity times
- **Context Switching Awareness**: Automatic buffer time to reduce cognitive load
- **Time Blocking**: Visual calendar view with drag-and-drop scheduling
- **Smart Suggestions**: Proactive task recommendations based on current context

### ADHD-Specific Features
- **Energy Level Matching**: Schedule high-energy tasks during your peak hours
- **Automatic Buffer Time**: Built-in breathing room between tasks
- **Context Switch Detection**: Minimize task switching and add recovery time
- **Flexible Time Estimates**: AI-powered duration prediction that learns from your patterns
- **Break Reminders**: Intelligent break suggestions to prevent burnout

### Apple Ecosystem Integration
- **Bidirectional Sync**: Two-way synchronization with Apple Reminders and Calendar
- **Per-Item Control**: Choose which tasks to sync with Apple services
- **Conflict Resolution**: Smart handling of changes made in multiple locations
- **Native Integration**: Uses macOS EventKit for seamless integration

### Privacy & Control
- **Local-First**: All data stored locally on your device
- **Offline Capable**: Core functionality works without internet
- **Configurable LLM**: Choose between Ollama (free, local), Gemini, or Claude
- **Your Data, Your Control**: Export and backup anytime

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Agent Framework**: LangGraph (orchestration and workflows)
- **LLM Integration**: LangChain (supports multiple providers)
- **LLM Providers**: Ollama (local), Google Gemini, Anthropic Claude
- **Database**: SQLite with SQLAlchemy ORM
- **Apple Integration**: PyObjC + EventKit framework
- **Language**: Python 3.10+

## Architecture Highlights

- **Supervisor Agent Pattern**: Coordinated multi-agent system with specialized agents
- **Repository Pattern**: Clean separation between business logic and data access
- **Provider Factory**: Pluggable LLM providers for flexibility
- **Modular Design**: Easily extensible for new features and capabilities

## Project Structure

```
adhd-planner/
├── README.md                 # This file
├── ARCHITECTURE.md           # Detailed system architecture
├── SETUP.md                  # Installation and setup guide
├── requirements.txt          # Python dependencies
├── docs/                     # Comprehensive documentation
│   ├── architecture/         # Architecture and design docs
│   ├── design/              # UI and workflow specifications
│   ├── technical/           # Technical implementation details
│   ├── implementation/      # Implementation guides
│   ├── operations/          # Error handling, security, performance
│   ├── user/                # End-user documentation
│   └── api/                 # Data schemas and APIs
└── src/                     # Source code (to be implemented)
    ├── agents/              # LangGraph agent implementations
    ├── graph/               # Graph state and workflow definitions
    ├── models/              # Data models (Pydantic)
    ├── services/            # Business logic services
    ├── repositories/        # Data access layer
    ├── integrations/        # Apple and LLM integrations
    ├── ui/                  # Streamlit user interface
    ├── database/            # Database schema and migrations
    └── utils/               # Utilities and helpers
```

## Quick Start

### Prerequisites
- macOS (required for Apple Reminders/Calendar integration)
- Python 3.10 or higher
- (Optional) Ollama for local LLM, or API keys for Gemini/Claude

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd adhd-planner

# Install dependencies (uv handles venv and Python automatically)
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
uv run python scripts/setup_database.py

# Run the application
uv run streamlit run src/ui/app.py
```

**Using uv** provides 10-100x faster dependency installation and automatic Python version management.

For detailed setup instructions, see [SETUP.md](SETUP.md).

## Documentation

### For Users
- [User Guide](docs/user/user-guide.md) - Getting started and using the application
- [Features Overview](docs/user/features.md) - Detailed feature descriptions

### For Developers
- [Architecture Documentation](ARCHITECTURE.md) - System design and architecture
- [Agent System Design](docs/architecture/agent-system.md) - LangGraph agent workflows
- [Data Models](docs/architecture/data-models.md) - Database schema and entities
- [Extension Guide](docs/technical/extension-guide.md) - Adding new features
- [Implementation Phases](docs/implementation/implementation-phases.md) - Development roadmap

### For Operations
- [Error Handling](docs/operations/error-handling.md) - Error strategies and logging
- [Security & Privacy](docs/operations/security-privacy.md) - Data protection
- [Performance](docs/operations/performance.md) - Optimization guidelines

## Specialized Agents

The system uses multiple specialized AI agents:

- **Supervisor Agent**: Routes requests and coordinates other agents
- **Planning Agent**: Extracts task details and estimates duration/energy
- **Scheduling Agent**: Generates ADHD-friendly schedules
- **Suggestion Agent**: Provides context-aware task recommendations
- **Sync Agent**: Manages bidirectional sync with Apple services
- **Energy Tracking Agent**: Learns your energy patterns over time

## Design Philosophy

### ADHD-First Design
Every feature is designed with ADHD challenges in mind:
- **Low friction**: Natural language input, minimal clicks
- **Visual clarity**: Clear task status, energy indicators, sync status
- **Flexibility**: Easily reschedule, modify estimates, disable sync
- **Forgiveness**: No penalties for changing plans or missing tasks
- **Self-awareness**: Insights into your patterns and behaviors

### Local-First
Your data stays on your device:
- **Privacy**: No cloud storage required
- **Speed**: Instant responses, no network latency
- **Reliability**: Works offline
- **Control**: Easy backups, exports, and migrations

### Extensible Framework
Built for reusability:
- **Modular architecture**: Clean separation of concerns
- **Pluggable components**: Easy to swap or extend
- **Clear interfaces**: Well-defined contracts between layers
- **Documentation-driven**: Comprehensive guides for extension

## Future Enhancements

Planned features for future releases:
- Multi-user support and collaboration
- Mobile app (iOS/Android)
- Voice interface for hands-free task management
- Gamification and habit tracking
- Integration with Google Calendar, Microsoft To Do, Notion
- Advanced analytics and productivity insights
- Focus timer with distraction tracking
- Accountability partner features

## Use Cases

### Daily Planning
"Plan my day" → AI generates an optimized schedule based on your tasks, energy patterns, and available time

### Quick Task Creation
"Add task: write report, 2 hours, high energy" → Creates task with intelligent defaults

### Energy-Aware Scheduling
System learns when you're most productive and schedules challenging tasks accordingly

### Sync with Apple Ecosystem
Tasks and time blocks automatically sync with Reminders and Calendar (configurable per-item)

### Smart Suggestions
"What should I work on now?" → AI considers time available, energy level, and task priorities

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[License information to be added]

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) for LLM integration
- [Streamlit](https://streamlit.io/) for the user interface
- [PyObjC](https://pyobjc.readthedocs.io/) for Apple integration

---

**Note**: This project is in active development. The architecture and documentation are complete, and implementation is in progress.
