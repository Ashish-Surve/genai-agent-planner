# User Workflows

## Overview

This document describes the key user workflows in ADHD Planner, showing step-by-step interactions and system responses.

## Table of Contents
1. [Task Creation Workflow](#task-creation-workflow)
2. [Schedule Generation Workflow](#schedule-generation-workflow)
3. [Bidirectional Sync Workflow](#bidirectional-sync-workflow)
4. [Energy Tracking Workflow](#energy-tracking-workflow)
5. [Task Completion Workflow](#task-completion-workflow)

## Task Creation Workflow

### Via Chat (Preferred Method)

**User Goal**: Create a new task using natural language

**Steps**:

1. **User Input**
   ```
   User types: "Add task: write quarterly report by Friday, probably 3 hours"
   ```

2. **Agent Processing**
   - Supervisor routes to Planning Agent
   - Planning Agent uses LLM to extract:
     - Title: "Write quarterly report"
     - Deadline: Friday (this week)
     - Estimated duration: 3 hours
     - Context: "work" (inferred)

3. **Agent Response**
   ```
   Agent: "Got it! I'll create a task to write quarterly report.

   Details:
   - Estimated time: 3 hours
   - Deadline: Friday, Jan 17 at 5pm
   - Energy needed: HIGH (writing/creative work)

   I noticed you're usually most focused in the mornings.
   Would you like me to schedule this for:

   Option 1: Thursday 9am-12pm (your peak energy time)
   Option 2: Friday 9am-12pm (day it's due)
   Option 3: Let me schedule it later

   Which works best?"
   ```

4. **User Selection**
   ```
   User clicks: "Option 1"
   ```

5. **Task Creation & Scheduling**
   - Task Service creates task
   - Calendar Service creates time block for Thu 9am-12pm
   - Sync Service queues for Apple Reminders (if enabled)

6. **Confirmation**
   ```
   Agent: "Perfect! I've created the task and scheduled it for
   Thursday 9-12pm. I've also synced it to your Apple Reminders.

   [View in Calendar] [View in Tasks]"
   ```

**Alternate Path**: Quick Creation
```
User: "Add write report"

Agent: "Added task 'write report'. How long do you think it will take?"

User: "2 hours"

Agent: "Got it! 2 hours. When's it due?"

User: "Friday"

Agent: (continues as above...)
```

### Via Tasks Page (Direct Entry)

**Steps**:

1. User clicks "+ New Task" button
2. Form modal appears:
   ```
   ┌─────────────────────────────────┐
   │ Create New Task                 │
   ├─────────────────────────────────┤
   │ Title: ___________________      │
   │ Description: _____________      │
   │ Estimated duration: [2] hours   │
   │ Deadline: [Jan 17] [5:00pm]     │
   │ Priority: [High ▾]              │
   │ Energy: [High ▾]                │
   │ □ Sync to Apple Reminders       │
   │                                 │
   │ [Cancel] [Create Task]          │
   └─────────────────────────────────┘
   ```
3. User fills form and clicks "Create Task"
4. Task created and appears in task list
5. Optional: Agent suggests scheduling

## Schedule Generation Workflow

### Full Day Planning

**User Goal**: Have the agent plan the entire day

**Steps**:

1. **User Request**
   ```
   User (in Chat): "Plan my day"
   ```

2. **Agent Data Gathering**
   - Scheduling Agent retrieves:
     - Incomplete tasks (from Task Service)
     - Existing calendar events (from Calendar Service)
     - User energy patterns (from Energy Service)
     - User preferences (buffer time, work hours, etc.)
   - Current data:
     ```
     Tasks to schedule:
     - Write report (3h, HIGH energy)
     - Code review (1h, MEDIUM energy)
     - Reply to emails (30min, LOW energy)
     - Team meeting (already scheduled 2pm-3pm)

     Energy pattern:
     - High: 9am-12pm
     - Medium: 12pm-2pm, 3pm-5pm
     - Low: 2pm-3pm (after lunch)

     Preferences:
     - 10min buffer between tasks
     - 45min max focus time before break
     ```

3. **Agent Schedule Generation**
   - Applies ADHD-friendly rules:
     - Match high-energy tasks to high-energy times
     - Add buffers between different task types
     - Include breaks after focus sessions
   - Generates 2-3 options using LLM

4. **Agent Presents Options**
   ```
   Agent: "I've created 3 schedule options for today:

   Option 1: FOCUS FIRST
   9:00-10:45   Write report (Part 1)
   10:45-11:00  BREAK
   11:00-12:00  Code review
   12:00-1:00   LUNCH
   1:00-2:00    Write report (Part 2)
   2:00-3:00    Team meeting
   3:00-3:30    Reply to emails

   Option 2: QUICK WINS FIRST
   9:00-10:00   Code review
   10:00-10:10  BUFFER
   10:10-11:10  Write report (Part 1)
   11:10-11:25  BREAK
   11:25-12:25  Write report (Part 2)
   12:25-1:30   LUNCH
   1:30-2:00    Reply to emails
   2:00-3:00    Team meeting

   Option 3: BALANCED
   9:00-10:30   Write report (Part 1)
   10:30-10:45  BREAK
   10:45-11:15  Reply to emails
   11:15-11:25  BUFFER
   11:25-12:25  Code review
   12:25-1:30   LUNCH
   1:30-2:00    Write report (Part 2)
   2:00-3:00    Team meeting

   Which option works best for you? (Or say 'customize' to modify)"
   ```

5. **User Selection**
   ```
   User: "Option 1"
   ```

6. **Schedule Creation**
   - Calendar Service creates all time blocks
   - Updates task scheduling metadata
   - Syncs to Apple Calendar (if enabled)

7. **Confirmation**
   ```
   Agent: "Done! I've planned your day with Option 1.
   You can view it in the Calendar tab.

   I'll send you a reminder 5 minutes before each task.
   Good luck! 💪

   [View Calendar] [Make Changes]"
   ```

### Single Task Scheduling

**User Goal**: Schedule just one task

**Steps**:

1. User (in Tasks page): Clicks "Schedule" button on task
2. Agent suggests times:
   ```
   Agent: "When would you like to work on 'Code review' (1h, MEDIUM energy)?

   Available slots today:
   - 10am-11am (HIGH energy - might be overkill)
   - 3pm-4pm (MEDIUM energy - good match!)
   - 4pm-5pm (MEDIUM energy)

   Recommendation: 3pm-4pm (matches your energy level)

   [Select 3pm-4pm] [Choose different time]"
   ```
3. User selects option
4. Time block created
5. Synced to calendar

## Bidirectional Sync Workflow

### Local to Apple (User creates task in ADHD Planner)

**Steps**:

1. User creates task in ADHD Planner with sync enabled
2. Task Service saves to local database
3. Sync Service detects new task
4. Creates SyncOperation (type: CREATE, direction: LOCAL_TO_APPLE)
5. Sync Agent processes operation:
   - Maps Task → EKReminder
   - Creates reminder in Apple Reminders
   - Stores `apple_reminder_id` in task
   - Updates `last_synced_at` timestamp
   - Sets `sync_status` to SYNCED
6. User sees sync indicator in UI: "🔄 Synced"

### Apple to Local (User creates reminder in Apple Reminders)

**Steps**:

1. Background: Sync Service polls Apple every N minutes
2. Sync Service detects new reminder in Apple
3. Creates SyncOperation (type: CREATE, direction: APPLE_TO_LOCAL)
4. Sync Agent processes:
   - Maps EKReminder → Task
   - Creates task in local database
   - Stores `apple_reminder_id`
   - Sets `sync_status` to SYNCED
5. User sees new task appear in Tasks page
6. Optional: Agent notifies in chat:
   ```
   Agent: "I noticed you added 'Buy groceries' in Apple Reminders.
   I've added it here too! Would you like me to help schedule it?"
   ```

### Conflict Resolution Workflow

**Scenario**: Same task modified in both places

**Steps**:

1. Sync Service detects conflict:
   - Local task modified at 2:00pm
   - Apple reminder modified at 2:05pm
   - Both modified since last sync (1:55pm)

2. Sync Agent analyzes conflict:
   ```
   Conflict detected for "Write report":

   Local version:
   - Title: "Write quarterly report"
   - Deadline: Friday 5pm
   - Modified: 2:00pm

   Apple version:
   - Title: "Write Q4 report"  (changed!)
   - Deadline: Friday 3pm  (changed!)
   - Modified: 2:05pm
   ```

3. Resolution Strategy (Last-Write-Wins by default):
   - Apple version is newer (2:05pm > 2:00pm)
   - Updates local task with Apple data
   - Sets sync_status to SYNCED

4. Optional: User notification for important conflicts:
   ```
   Agent: "I noticed conflicting changes to 'Write report'.

   You changed the title in ADHD Planner, but also changed
   the deadline in Apple Reminders.

   I've merged the changes using the latest from each.
   Current state:
   - Title: "Write Q4 report" (from Apple, newer)
   - Deadline: Friday 3pm (from Apple, newer)

   [Accept] [Undo] [Edit manually]"
   ```

## Energy Tracking Workflow

### Passive Tracking

**Automatic data collection**:

1. **Task Completion**
   - User completes task at 11:30am
   - System logs:
     ```
     {
       timestamp: 11:30am,
       task_completed: "Code review",
       actual_duration: 65 min (vs 60 min estimated),
       time_of_day: "late morning",
       context_switches_during_task: 2
     }
     ```

2. **Pattern Analysis (Background)**
   - Energy Agent runs nightly
   - Analyzes completion patterns:
     - "User consistently completes high-energy tasks 9-12am"
     - "Tasks after 2pm often take longer than estimated"
     - "Completion rate drops after 3 context switches"

3. **Profile Update**
   - Updates UserPreferences with discovered patterns
   - Improves future predictions

### Active Tracking

**User self-reporting**:

1. **Check-in Prompt**
   ```
   Agent (at 10am): "Quick check-in: How's your energy right now?

   [⚡ High] [~ Medium] [😴 Low]"
   ```

2. **User Response**
   - User selects "Medium"

3. **Logging**
   - Creates EnergyLog entry:
     ```
     {
       timestamp: 10:00am,
       reported_energy: MEDIUM,
       predicted_energy: HIGH,
       energy_accuracy: 0.5,  // Prediction was off
       tasks_completed_today: 1,
       context_switches: 2,
       time_since_break: 45min
     }
     ```

4. **Learning**
   - Energy Agent notes prediction was wrong
   - Adjusts model for better future predictions

5. **Immediate Suggestion**
   ```
   Agent: "Thanks! Since your energy is medium, I'd suggest:

   1. Code review (1h, MEDIUM) - good match!
   2. Reply to emails (30min, LOW) - save energy

   Skip the 'Write report' task for now (needs HIGH energy).

   [Start Code Review] [See All Tasks]"
   ```

## Task Completion Workflow

### Marking Complete

**Steps**:

1. **User Action**
   - Checks box next to task in Tasks page
   - OR says in chat: "I finished the code review"

2. **System Processing**
   - Records completion time
   - Calculates actual duration
   - Updates task status to COMPLETED

3. **Data Collection**
   ```
   Task: Code review
   Estimated: 60 min
   Actual: 55 min
   Completed at: 11:30am (late morning, high energy time)
   Accuracy: 92% (good estimate!)
   ```

4. **Sync to Apple**
   - If sync enabled:
     - Updates Apple Reminder completion status
     - Sets completion date

5. **Agent Response**
   ```
   Agent: "Nice work finishing the code review! 🎉

   You completed it in 55 minutes (estimated 60 min).
   Your estimates are getting better!

   You have 30 minutes before lunch. Want a suggestion
   for what to do next?"
   ```

6. **Learning**
   - Energy Agent updates patterns
   - Time Estimation Service refines algorithms
   - User's completion history grows

### Viewing Completed Tasks

**Steps**:

1. User goes to Tasks page
2. Clicks "✓ COMPLETED (5)" to expand section
3. Sees completed tasks:
   ```
   ✓ Code review - Completed today at 11:30am (55min)
   ✓ Team standup - Completed today at 9:30am (30min)
   ✓ Reply to client - Completed yesterday (15min)
   ...
   ```

4. Can click task to see details/analytics

## Edge Cases & Error Handling

### Sync Failure Workflow

1. Sync operation fails (network issue, permission denied, etc.)
2. Sync status changes to ERROR
3. Error logged with details
4. User sees indicator: "❌ Sync Failed"
5. Click for details:
   ```
   Sync Error: Permission denied for Apple Reminders

   This task couldn't be synced to Apple Reminders.

   [Grant Permission] [Retry Sync] [Disable Sync for This Task]
   ```

### Overdue Task Workflow

1. Background process checks for overdue tasks
2. Finds task with deadline in past
3. Marks with visual indicator (red border)
4. Agent proactive message:
   ```
   Agent: "Heads up: 'Write report' was due yesterday.

   Would you like to:
   1. Reschedule it for today
   2. Mark as complete (if you finished it)
   3. Cancel it (if no longer needed)

   [Reschedule] [Mark Complete] [Cancel]"
   ```

### Calendar Conflict Workflow

1. User tries to schedule task
2. System detects overlap with existing time block
3. Shows conflict:
   ```
   Conflict: There's already a time block scheduled for 2-3pm
   (Team meeting)

   Available alternatives:
   - 3pm-4pm
   - 4pm-5pm
   - Tomorrow 9am-10am

   [Choose Alternative] [Override (not recommended)]"
   ```

## Related Documentation

- [UI Specifications](ui-specifications.md)
- [ADHD Features](adhd-features.md)
- [Agent Workflows](../architecture/agent-system.md#agent-workflows)
