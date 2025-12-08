# Integration Design

## Overview

This document describes the integration architecture for ADHD Planner, covering Apple ecosystem integration (Reminders and Calendar) and LLM provider abstraction.

## Table of Contents
1. [Apple Integration](#apple-integration)
2. [LLM Provider Abstraction](#llm-provider-abstraction)
3. [Sync Architecture](#sync-architecture)
4. [Conflict Resolution](#conflict-resolution)

## Apple Integration

### Technology Stack

**PyObjC + EventKit Framework**

- **PyObjC**: Python bridge to Objective-C frameworks
- **EventKit**: Apple framework for accessing Calendar and Reminders
- **Platform**: macOS only (iOS support possible but not planned)

### Architecture

```
┌──────────────────────────────────────┐
│   ADHD Planner Services              │
│  (Task Service, Calendar Service)    │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│      Sync Service                    │
│  (Orchestrates sync operations)      │
└────────────────┬─────────────────────┘
                 │
          ┌──────┴──────┐
          ▼             ▼
┌──────────────┐  ┌──────────────┐
│  Reminders   │  │  Calendar    │
│  Integration │  │  Integration │
└──────┬───────┘  └──────┬───────┘
       │                 │
       │  PyObjC         │  PyObjC
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  EventKit    │  │  EventKit    │
│ EKReminder   │  │  EKEvent     │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌────────────────────────────────────┐
│   Apple Reminders / Calendar App   │
└────────────────────────────────────┘
```

## Apple Reminders Integration

### Capabilities

- Create, read, update, delete reminders
- Set due dates and priorities
- Add notes and URLs
- Organize in lists
- Set completion status

### Data Mapping

```
Task (ADHD Planner) → EKReminder (Apple)
├── title → title
├── description → notes
├── deadline → dueDateComponents
├── priority → priority (mapped)
├── completed_at → completionDate
├── tags → stored in notes (formatted)
└── apple_reminder_id → calendarItemIdentifier
```

### Priority Mapping

```python
# ADHD Planner → Apple Reminders
Priority.URGENT → EKReminderPriority.High (1)
Priority.HIGH → EKReminderPriority.Medium (5)
Priority.MEDIUM → EKReminderPriority.Low (9)
Priority.LOW → EKReminderPriority.None (0)
```

### Implementation Example

```python
from EventKit import EKEventStore, EKReminder, EKEntityTypeReminder

class RemindersIntegration:
    def __init__(self):
        self.store = EKEventStore.alloc().init()
        self._request_access()

    def _request_access(self):
        """Request access to Reminders"""
        granted, error = self.store.requestAccessToEntityType_completion_(
            EKEntityTypeReminder,
            None
        )
        if not granted:
            raise PermissionError("Reminders access denied")

    def create_reminder(self, task: Task) -> str:
        """Create Apple Reminder from Task"""
        reminder = EKReminder.reminderWithEventStore_(self.store)

        # Basic properties
        reminder.setTitle_(task.title)
        if task.description:
            reminder.setNotes_(task.description)

        # Due date
        if task.deadline:
            components = self._datetime_to_components(task.deadline)
            reminder.setDueDateComponents_(components)

        # Priority
        priority = self._map_priority(task.priority)
        reminder.setPriority_(priority)

        # Save
        reminder.setCalendar_(self.store.defaultCalendarForNewReminders())
        success, error = self.store.saveReminder_commit_error_(
            reminder, True, None
        )

        if success:
            return reminder.calendarItemIdentifier()
        else:
            raise Exception(f"Failed to create reminder: {error}")

    def fetch_reminder(self, reminder_id: str) -> EKReminder:
        """Fetch reminder by ID"""
        return self.store.calendarItemWithIdentifier_(reminder_id)

    def update_reminder(self, reminder_id: str, task: Task):
        """Update existing reminder"""
        reminder = self.fetch_reminder(reminder_id)
        if not reminder:
            raise ValueError(f"Reminder {reminder_id} not found")

        # Update properties
        reminder.setTitle_(task.title)
        reminder.setNotes_(task.description or "")

        if task.deadline:
            components = self._datetime_to_components(task.deadline)
            reminder.setDueDateComponents_(components)

        # Save changes
        success, error = self.store.saveReminder_commit_error_(
            reminder, True, None
        )
        if not success:
            raise Exception(f"Failed to update reminder: {error}")

    def delete_reminder(self, reminder_id: str):
        """Delete reminder"""
        reminder = self.fetch_reminder(reminder_id)
        if reminder:
            self.store.removeReminder_commit_error_(reminder, True, None)

    def fetch_all_reminders(self) -> List[EKReminder]:
        """Fetch all incomplete reminders"""
        predicate = self.store.predicateForRemindersInCalendars_(None)
        reminders = []

        def completion_handler(reminder_list):
            reminders.extend(reminder_list)

        self.store.fetchRemindersMatchingPredicate_completion_(
            predicate,
            completion_handler
        )

        return reminders
```

## Apple Calendar Integration

### Capabilities

- Create, read, update, delete calendar events
- Set start/end times
- Add alerts/alarms
- Set recurrence rules
- Add location and notes

### Data Mapping

```
TimeBlock (ADHD Planner) → EKEvent (Apple Calendar)
├── task.title → title
├── start_time → startDate
├── end_time → endDate
├── notes → notes
├── apple_calendar_event_id → eventIdentifier
└── reminders → alarms (converted)
```

### Implementation Example

```python
from EventKit import EKEvent, EKAlarm, EKRecurrenceRule, EKEntityTypeEvent

class CalendarIntegration:
    def __init__(self):
        self.store = EKEventStore.alloc().init()
        self._request_access()

    def _request_access(self):
        """Request access to Calendar"""
        granted, error = self.store.requestAccessToEntityType_completion_(
            EKEntityTypeEvent,
            None
        )
        if not granted:
            raise PermissionError("Calendar access denied")

    def create_event(self, time_block: TimeBlock, task: Optional[Task] = None) -> str:
        """Create Calendar event from TimeBlock"""
        event = EKEvent.eventWithEventStore_(self.store)

        # Basic properties
        if task:
            event.setTitle_(task.title)
            event.setNotes_(task.description or "")
        else:
            event.setTitle_(f"{time_block.block_type.value.title()} Time")

        # Time
        event.setStartDate_(time_block.start_time)
        event.setEndDate_(time_block.end_time)

        # Calendar
        event.setCalendar_(self.store.defaultCalendarForNewEvents())

        # Alerts (15 min before by default)
        alarm = EKAlarm.alarmWithRelativeOffset_(-15 * 60)
        event.addAlarm_(alarm)

        # Save
        success, error = self.store.saveEvent_span_commit_error_(
            event, 0, True, None  # 0 = this event only
        )

        if success:
            return event.eventIdentifier()
        else:
            raise Exception(f"Failed to create event: {error}")

    def fetch_events(self, start_date: datetime, end_date: datetime) -> List[EKEvent]:
        """Fetch events in date range"""
        calendars = [self.store.defaultCalendarForNewEvents()]
        predicate = self.store.predicateForEventsWithStartDate_endDate_calendars_(
            start_date, end_date, calendars
        )

        return self.store.eventsMatchingPredicate_(predicate)

    def update_event(self, event_id: str, time_block: TimeBlock):
        """Update existing event"""
        event = self.store.eventWithIdentifier_(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")

        # Update times
        event.setStartDate_(time_block.start_time)
        event.setEndDate_(time_block.end_time)

        # Save
        success, error = self.store.saveEvent_span_commit_error_(
            event, 0, True, None
        )
        if not success:
            raise Exception(f"Failed to update event: {error}")

    def delete_event(self, event_id: str):
        """Delete event"""
        event = self.store.eventWithIdentifier_(event_id)
        if event:
            self.store.removeEvent_span_commit_error_(event, 0, True, None)
```

### Permission Handling

```python
class PermissionManager:
    @staticmethod
    def request_reminders_access() -> bool:
        """Request access to Reminders"""
        store = EKEventStore.alloc().init()
        granted, error = store.requestAccessToEntityType_completion_(
            EKEntityTypeReminder, None
        )
        return granted

    @staticmethod
    def request_calendar_access() -> bool:
        """Request access to Calendar"""
        store = EKEventStore.alloc().init()
        granted, error = store.requestAccessToEntityType_completion_(
            EKEntityTypeEvent, None
        )
        return granted

    @staticmethod
    def check_permissions() -> dict:
        """Check current permission status"""
        store = EKEventStore.alloc().init()
        return {
            "reminders": store.authorizationStatusForEntityType_(
                EKEntityTypeReminder
            ),
            "calendar": store.authorizationStatusForEntityType_(
                EKEntityTypeEvent
            )
        }
```

## LLM Provider Abstraction

### Provider Interface

```python
from abc import ABC, abstractmethod
from typing import Iterator

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate completion from prompt"""
        pass

    @abstractmethod
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Stream completion tokens"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass
```

### Ollama Provider

```python
from langchain_ollama import OllamaLLM

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str, temperature: float = 0.7):
        self.llm = OllamaLLM(
            base_url=base_url,
            model=model,
            temperature=temperature
        )

    def generate(self, prompt: str, **kwargs) -> str:
        return self.llm.invoke(prompt, **kwargs)

    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        for chunk in self.llm.stream(prompt, **kwargs):
            yield chunk

    def is_available(self) -> bool:
        try:
            # Test connection
            self.llm.invoke("test")
            return True
        except Exception:
            return False
```

### Gemini Provider

```python
from langchain_google_genai import GoogleGenerativeAI

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        self.llm = GoogleGenerativeAI(
            google_api_key=api_key,
            model=model,
            temperature=temperature
        )

    def generate(self, prompt: str, **kwargs) -> str:
        return self.llm.invoke(prompt, **kwargs)

    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        for chunk in self.llm.stream(prompt, **kwargs):
            yield chunk

    def is_available(self) -> bool:
        try:
            self.llm.invoke("test")
            return True
        except Exception:
            return False
```

### Claude Provider

```python
from langchain_anthropic import ChatAnthropic

class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        self.llm = ChatAnthropic(
            anthropic_api_key=api_key,
            model=model,
            temperature=temperature
        )

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.llm.invoke(prompt, **kwargs)
        return response.content

    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        for chunk in self.llm.stream(prompt, **kwargs):
            yield chunk.content

    def is_available(self) -> bool:
        try:
            self.llm.invoke("test")
            return True
        except Exception:
            return False
```

### Provider Factory

```python
class LLMProviderFactory:
    @staticmethod
    def create(provider_name: str, **config) -> LLMProvider:
        """Factory method to create LLM provider"""

        if provider_name == "ollama":
            return OllamaProvider(
                base_url=config.get("base_url", "http://localhost:11434"),
                model=config.get("model", "llama3.1"),
                temperature=config.get("temperature", 0.7)
            )

        elif provider_name == "gemini":
            if not config.get("api_key"):
                raise ValueError("Gemini requires API key")
            return GeminiProvider(
                api_key=config["api_key"],
                model=config.get("model", "gemini-pro"),
                temperature=config.get("temperature", 0.7)
            )

        elif provider_name == "claude":
            if not config.get("api_key"):
                raise ValueError("Claude requires API key")
            return ClaudeProvider(
                api_key=config["api_key"],
                model=config.get("model", "claude-3-5-sonnet-20241022"),
                temperature=config.get("temperature", 0.7)
            )

        else:
            raise ValueError(f"Unknown provider: {provider_name}")
```

## Sync Architecture

### Sync Strategies

**1. One-Way (Local → Apple)**
- Local is source of truth
- Changes only pushed to Apple
- Useful for users who prefer to manage in ADHD Planner

**2. One-Way (Apple → Local)**
- Apple is source of truth
- Changes only pulled from Apple
- Useful for users who prefer Apple apps

**3. Two-Way (Bidirectional)**
- Changes flow both directions
- Conflict resolution required
- Most flexible but complex

### Sync Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Sync Service                             │
│                                                             │
│  Responsibilities:                                          │
│  - Detect local changes                                     │
│  - Poll Apple for changes                                   │
│  - Queue sync operations                                    │
│  - Invoke Sync Agent                                        │
│  - Handle errors and retries                                │
└──────────────┬──────────────────────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
┌──────────────┐  ┌──────────────┐
│ Local → Apple│  │Apple → Local │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
  Create SyncOperation
       │
       ▼
  Process in background
       │
       ▼
  Update sync metadata
```

### Sync Operation Lifecycle

```
1. Change Detected
   ↓
2. Create SyncOperation (status=PENDING)
   ↓
3. Queue for processing
   ↓
4. Sync Agent processes
   ↓
5. IF success:
      status=SYNCED
      completed_at=now
   ELIF conflict:
      status=CONFLICT
      Invoke conflict resolution
   ELSE:
      status=ERROR
      retry_count++
      Schedule retry
```

### Per-Item Sync Control

```python
class Task:
    sync_enabled: bool  # Master switch for this task

def should_sync_task(task: Task, user_prefs: UserPreferences) -> bool:
    """Determine if task should sync"""

    # Explicit disable takes precedence
    if not task.sync_enabled:
        return False

    # User global preference
    if not user_prefs.default_sync_to_reminders:
        return False

    # Otherwise, sync
    return True
```

## Conflict Resolution

### Conflict Detection

```python
def detect_conflict(local_task: Task, apple_reminder: EKReminder) -> bool:
    """Check if task and reminder conflict"""

    local_timestamp = local_task.updated_at
    apple_timestamp = apple_reminder.lastModifiedDate()

    # If both modified since last sync
    if (local_timestamp > local_task.last_synced_at and
        apple_timestamp > local_task.last_synced_at):

        # And content differs
        if task_differs_from_reminder(local_task, apple_reminder):
            return True

    return False
```

### Resolution Strategies

**1. Last-Write-Wins (Default)**
```python
def resolve_last_write_wins(local_task: Task, apple_reminder: EKReminder):
    """Use most recently modified version"""

    if local_task.updated_at > apple_reminder.lastModifiedDate():
        # Local is newer - push to Apple
        update_reminder(apple_reminder, local_task)
    else:
        # Apple is newer - pull to local
        update_task(local_task, apple_reminder)
```

**2. User Prompt (For Important Conflicts)**
```python
def resolve_with_user(local_task: Task, apple_reminder: EKReminder):
    """Ask user to choose version"""

    # Present both versions to user
    choice = prompt_user_for_conflict_resolution(
        local_version=local_task,
        apple_version=apple_reminder
    )

    if choice == "local":
        update_reminder(apple_reminder, local_task)
    elif choice == "apple":
        update_task(local_task, apple_reminder)
    elif choice == "merge":
        merged = merge_task_and_reminder(local_task, apple_reminder)
        update_both(merged)
```

**3. Field-Level Merge**
```python
def merge_task_and_reminder(local_task: Task, apple_reminder: EKReminder) -> Task:
    """Merge non-conflicting fields"""

    merged = Task()

    # Title: use local if changed, else apple
    merged.title = (local_task.title if local_task.title != original.title
                    else convert_title(apple_reminder.title()))

    # Deadline: use newer
    merged.deadline = max(local_task.deadline, convert_date(apple_reminder.dueDateComponents()))

    # Priority: use higher priority
    merged.priority = max(local_task.priority, convert_priority(apple_reminder.priority()))

    return merged
```

## Error Handling

### Retry Logic

```python
class SyncService:
    MAX_RETRIES = 3
    RETRY_DELAYS = [60, 300, 900]  # seconds: 1min, 5min, 15min

    async def process_sync_operation(self, operation: SyncOperation):
        """Process sync with retry logic"""

        try:
            if operation.direction == SyncDirection.LOCAL_TO_APPLE:
                await self._sync_to_apple(operation)
            else:
                await self._sync_from_apple(operation)

            operation.status = SyncStatus.SYNCED
            operation.completed_at = datetime.now()

        except Exception as e:
            operation.retry_count += 1

            if operation.retry_count <= self.MAX_RETRIES:
                # Schedule retry
                delay = self.RETRY_DELAYS[operation.retry_count - 1]
                schedule_retry(operation, delay)
                operation.status = SyncStatus.PENDING
            else:
                # Max retries exceeded
                operation.status = SyncStatus.ERROR
                operation.error_message = str(e)
                logger.error(f"Sync failed after {self.MAX_RETRIES} retries: {e}")
```

## Related Documentation

- [System Overview](system-overview.md)
- [Data Models](data-models.md)
- [Apple Integration Implementation](../technical/extension-guide.md#adding-new-sync-integrations)
- [LLM Service](../technical/extension-guide.md#adding-new-llm-providers)
