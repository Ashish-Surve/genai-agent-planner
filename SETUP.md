# ADHD Planner - Setup Guide

## Current Implementation Status

**✅ ADHD-1 Complete (Foundation)**
- Project structure and package setup
- Configuration management with environment variables
- Logging infrastructure
- Testing framework with pytest
- Code quality tools (ruff, black, mypy)

**🚧 In Progress**
- ADHD-2: Database Schema & Migrations (next)
- Full application features coming in subsequent stories

**Note**: The application is under active development. Follow the [implementation progress](.jira/README.md) to track completion of features.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [LLM Provider Setup](#llm-provider-setup)
5. [Apple Integration Setup](#apple-integration-setup)
6. [Running the Application](#running-the-application)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: macOS 10.15 (Catalina) or later
  - Required for Apple Reminders/Calendar integration via EventKit
  - Linux/Windows support possible but without Apple integration
- **Python**: 3.10 or higher (uv will install automatically if needed)
- **Disk Space**: ~500MB for dependencies and database
- **RAM**: Minimum 4GB (8GB+ recommended for local LLM)

### Required Software

**uv** - Modern, fast Python package manager
- **Install uv** (recommended method):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Or via Homebrew**:
  ```bash
  brew install uv
  ```
- **Or via pip**:
  ```bash
  pip install uv
  ```
- Documentation: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

**Git** - Version control
- Install: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- Or via Homebrew: `brew install git`

**Note**: `uv` will automatically install the correct Python version (3.10+) if not already present.

### Optional Software
- **Ollama** (for local LLM) - [Download](https://ollama.ai/)
- **VS Code** or preferred IDE
- **iTerm2** or preferred terminal (macOS)

### LLM Provider Options (choose one or more)

**Option 1: Ollama (Free, Local, Privacy-focused)**
- Install Ollama: `brew install ollama` or download from [ollama.ai](https://ollama.ai/)
- No API key required
- Runs entirely on your machine
- Recommended model: `llama3.1` or `llama3.2`

**Option 2: Google Gemini (API-based)**
- Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Free tier available
- Good balance of cost and quality

**Option 3: Anthropic Claude (API-based)**
- Get API key from [Anthropic Console](https://console.anthropic.com/)
- Paid service (pay-per-use)
- Highest quality responses

## Installation

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Ashish-Surve/genai-agent-planner.git
cd genai-agent-planner
```

### 2. Install Dependencies with uv

```bash
# uv will automatically:
# - Create a virtual environment (.venv)
# - Install Python 3.10+ if needed
# - Install all dependencies from pyproject.toml
# - Install development tools (pytest, ruff, black, mypy)

uv sync --extra dev

# This creates .venv/ and installs all dependencies
```

**What just happened?**
- `uv sync` read `pyproject.toml`
- Created a `.venv/` directory
- Installed Python 3.10+ (if not available)
- Installed all project dependencies including dev tools
- Created a `uv.lock` file for reproducible builds

### 3. Verify Installation

```bash
# Check Python version (should be 3.10+)
uv run python --version

# Verify package imports work
uv run python -c "from adhd_planner.utils.config import get_settings; print('✓ Installation successful')"

# Run tests to verify setup
uv run pytest tests/ -v

# Check code quality tools
uv run ruff check src/ tests/
uv run black --check src/ tests/
```

## Configuration

### 1. Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
code .env
```

### 2. Configure Environment Variables

Edit `.env` with the following settings:

```bash
# ===== LLM CONFIGURATION =====

# Choose: ollama, gemini, or claude
LLM_PROVIDER=ollama

# Ollama settings (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Gemini settings (if using Gemini)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro

# Claude settings (if using Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# ===== DATABASE CONFIGURATION =====

DATABASE_PATH=data/database/adhd_planner.db

# ===== SYNC CONFIGURATION =====

# Enable/disable sync with Apple
SYNC_ENABLED=true

# Sync interval in minutes
SYNC_INTERVAL_MINUTES=5

# ===== LOGGING CONFIGURATION =====

LOG_LEVEL=INFO
LOG_FILE=data/logs/app.log

# ===== STREAMLIT CONFIGURATION =====

STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_THEME_BASE=light
```

### 3. Create Data Directories

```bash
# Create necessary directories
mkdir -p data/database
mkdir -p data/config
mkdir -p data/logs

# Verify directory structure
ls -la data/
```

## LLM Provider Setup

### Option 1: Ollama (Recommended for beginners)

#### Install Ollama

```bash
# On macOS
brew install ollama

# Or download from https://ollama.ai/

# Verify installation
ollama --version
```

#### Start Ollama Service

```bash
# Start Ollama (runs in background)
ollama serve

# In a new terminal, pull recommended model
ollama pull llama3.1

# Verify model is available
ollama list
```

#### Test Ollama

```bash
# Test the model
ollama run llama3.1 "Hello, how are you?"

# Should get a response from the model
```

#### Configure for ADHD Planner

```bash
# Edit .env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### Option 2: Google Gemini

#### Get API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the API key

#### Configure for ADHD Planner

```bash
# Edit .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-pro
```

#### Test API Key

```bash
# Run test script
uv run python scripts/test_llm_connection.py

# Should see successful connection message
```

### Option 3: Anthropic Claude

#### Get API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or sign in
3. Navigate to API Keys
4. Create new key
5. Copy the API key

#### Configure for ADHD Planner

```bash
# Edit .env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your_actual_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

#### Test API Key

```bash
# Run test script
uv run python scripts/test_llm_connection.py

# Should see successful connection message
```

## Apple Integration Setup

### 1. Request Permissions

The first time you run the app, macOS will ask for permissions to access:
- **Reminders**: To sync tasks
- **Calendar**: To sync time blocks

### 2. Grant Permissions

1. Click "OK" when prompted
2. Or manually grant in System Settings:
   - Go to **System Settings → Privacy & Security → Reminders**
   - Enable access for Terminal and Python
   - Go to **System Settings → Privacy & Security → Calendar**
   - Enable access for Terminal and Python

### 3. Test Permissions

```bash
# Run permission test script
uv run python scripts/test_apple_permissions.py

# Should output:
# ✓ Reminders access: Granted
# ✓ Calendar access: Granted
```

### 4. Configure Default Calendar/List

Edit user preferences (after first run) to specify:
- Which Apple Reminders list to sync with
- Which Apple Calendar to sync with

## Running the Application

### Current Status: Foundation Complete

**What works now:**
- Configuration loading from `.env` file
- Logging to console and file
- All tests passing
- Code quality checks

**Coming soon:**
- Database initialization (ADHD-2)
- Streamlit UI (ADHD-17+)
- Full application features

### Test Current Setup

```bash
# Test configuration loading
uv run python -c "from adhd_planner.utils.config import get_settings; s = get_settings(); print(f'✓ Config loaded: LLM={s.llm_provider}')"

# Test logging
uv run python -c "from adhd_planner.utils.logger import logger; logger.info('Test log message'); print('✓ Logging works')"

# Run all tests
uv run pytest tests/ -v --cov=src

# Check logs were created
ls -lh data/logs/app.log
cat data/logs/app.log
```

### Once UI is Implemented (Coming Soon)

```bash
# Start Streamlit app with uv (will be available after ADHD-17)
uv run streamlit run src/adhd_planner/ui/app.py

# Application should open in browser automatically
# Or navigate to: http://localhost:8501
```

## Verification

### Current Setup Verification (ADHD-1)

Verify the foundation is working correctly:

- [ ] Dependencies installed: `uv run python --version` shows 3.10+
- [ ] Configuration loads: `uv run python -c "from adhd_planner.utils.config import get_settings; print('✓')"`
- [ ] Logging works: Check `data/logs/app.log` exists and has entries
- [ ] Tests pass: `uv run pytest tests/ -v` shows 3/3 passed
- [ ] Linting passes: `uv run ruff check src/ tests/` shows no errors
- [ ] Formatting passes: `uv run black --check src/ tests/` shows all files formatted

### Check Configuration Values

```bash
# View current configuration
uv run python << 'EOF'
from adhd_planner.utils.config import get_settings
s = get_settings()
print(f"LLM Provider: {s.llm_provider}")
print(f"Database Path: {s.database_path}")
print(f"Log Level: {s.log_level}")
print(f"Max Focus Duration: {s.max_focus_duration} min")
EOF
```

### Check Logs

```bash
# View application logs
cat data/logs/app.log

# Or follow logs in real-time
tail -f data/logs/app.log
```

### Future Verification (After ADHD-2+)

Once more stories are complete, you'll be able to:
- [ ] Initialize database and create tables
- [ ] Create tasks via chat interface
- [ ] View tasks in calendar
- [ ] Sync with Apple Reminders/Calendar

## Troubleshooting

### uv Command Not Found

**Problem**: `uv: command not found`

**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv

# Add to PATH (if needed)
export PATH="$HOME/.cargo/bin:$PATH"

# Verify installation
uv --version
```

### Python Version Issues

**Problem**: Wrong Python version

**Solution**:
```bash
# uv can install Python for you
uv python install 3.10

# Or specify Python version explicitly
uv venv --python 3.10

# Or use system Python 3.10+
uv venv --python python3.10
```

### Dependency Installation Issues

**Problem**: Packages not installing correctly

**Solution**:
```bash
# Remove lock file and resync
rm uv.lock
uv sync

# Or force reinstall
uv sync --reinstall

# Clear uv cache if needed
uv cache clean
```

### Virtual Environment Issues

**Problem**: Virtual environment not working

**Solution**:
```bash
# Remove and recreate .venv
rm -rf .venv
uv sync

# Verify venv creation
ls -la .venv/

# Activate manually
source .venv/bin/activate
```

### Ollama Connection Issues

**Problem**: `Connection refused` to Ollama

**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve

# Check if model is downloaded
ollama list

# Pull model if missing
ollama pull llama3.1
```

### API Key Issues

**Problem**: `Invalid API key` error

**Solution**:
```bash
# Verify API key in .env (no quotes, no spaces)
cat .env | grep API_KEY

# Test API key directly
uv run python scripts/test_llm_connection.py

# Regenerate key from provider console if needed
```

### Apple Permissions Issues

**Problem**: Cannot access Reminders or Calendar

**Solution**:
```bash
# Reset permissions
tccutil reset Reminders
tccutil reset Calendar

# Run app again - will re-prompt for permissions

# Or manually grant in System Settings
# System Settings → Privacy & Security
```

### Database Issues

**Problem**: Database errors or corruption

**Solution**:
```bash
# Backup existing database
cp data/database/adhd_planner.db data/database/adhd_planner.db.backup

# Recreate database
rm data/database/adhd_planner.db
uv run python scripts/setup_database.py

# Restore from backup if needed
```

### Port Already in Use

**Problem**: `Port 8501 is already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or use different port
uv run streamlit run src/ui/app.py --server.port 8502
```

### Import Errors

**Problem**: `ModuleNotFoundError` for installed packages

**Solution**:
```bash
# Resync dependencies
uv sync --reinstall

# Or check if venv is activated
source .venv/bin/activate
which python  # Should show .venv path

# Reinstall specific package
uv pip install <package-name> --force-reinstall
```

## Advanced Configuration

### Using Different Python Versions

```bash
# Install specific Python version with uv
uv python install 3.11

# Create venv with specific Python
uv venv --python 3.11

# Sync dependencies
uv sync
```

### Adding New Dependencies

```bash
# Add a new package
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# This automatically updates pyproject.toml and uv.lock
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add <package-name>@latest

# Check for outdated packages
uv pip list --outdated
```

### Custom Streamlit Config

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#6366f1"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f3f4f6"
textColor = "#1f2937"
font = "sans serif"

[server]
port = 8501
headless = false
address = "localhost"

[browser]
gatherUsageStats = false
```

### Database Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## Production Deployment

For running in production (always-on):

### 1. Use Process Manager

```bash
# Install PM2 (Node.js process manager)
npm install -g pm2

# Create start script
cat > start.sh << 'EOF'
#!/bin/bash
source .venv/bin/activate
streamlit run src/ui/app.py
EOF

chmod +x start.sh

# Start with PM2
pm2 start start.sh --name adhd-planner
pm2 save
pm2 startup  # Enable on boot
```

### 2. Run in Background

```bash
# Using nohup
nohup uv run streamlit run src/ui/app.py &

# Or using screen
screen -S adhd-planner
uv run streamlit run src/ui/app.py
# Ctrl+A, D to detach
```

## Next Steps

After successful setup:

1. **Customize Settings**: Go to Settings page and configure your preferences
2. **Set Energy Patterns**: Define your typical high/low energy times
3. **Import Existing Tasks**: Use chat to add your current to-dos
4. **Configure Sync**: Enable/disable sync for specific tasks
5. **Read User Guide**: See [User Guide](docs/user/user-guide.md) for detailed usage

## Getting Help

If you encounter issues not covered here:

1. Check [Troubleshooting](#troubleshooting) section above
2. Review logs in `data/logs/app.log`
3. Search existing GitHub issues
4. Open a new issue with:
   - Error message
   - Steps to reproduce
   - System information (`uv --version`, `uv run python --version`)
   - Relevant log excerpts

## Useful Commands Reference

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Add new package
uv add <package-name>

# Update dependencies
uv sync --upgrade

# Run Python script
uv run python <script.py>

# Start application
uv run streamlit run src/ui/app.py

# Activate virtual environment
source .venv/bin/activate

# View logs
tail -f data/logs/app.log

# Test LLM connection
uv run python scripts/test_llm_connection.py

# Test Apple permissions
uv run python scripts/test_apple_permissions.py

# Reset database
uv run python scripts/setup_database.py --reset

# Backup database
cp data/database/adhd_planner.db backups/adhd_planner_$(date +%Y%m%d).db

# Check outdated packages
uv pip list --outdated
```

## Why uv?

**uv** is a modern, blazing-fast Python package manager that offers:

- **Speed**: 10-100x faster than pip
- **Reliability**: Deterministic installs with `uv.lock`
- **Simplicity**: Manages Python versions, venvs, and packages
- **Compatibility**: Drop-in replacement for pip/venv
- **Modern**: Works seamlessly with `pyproject.toml`

Learn more: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

## Uninstallation

If you want to remove ADHD Planner:

```bash
# 1. Stop the application (Ctrl+C)

# 2. Remove directory
cd ..
rm -rf adhd-planner

# 3. (Optional) Revoke Apple permissions
# System Settings → Privacy & Security
# Remove permissions for Reminders and Calendar

# 4. (Optional) Remove uv (if desired)
rm -rf ~/.cargo/bin/uv
```

Your Apple Reminders and Calendar data will remain intact.
