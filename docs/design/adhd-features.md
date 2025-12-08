# ADHD-Specific Features

## Overview

This document describes features specifically designed to address ADHD-related challenges in task management and productivity.

## Table of Contents
1. [Energy Level Tracking](#energy-level-tracking)
2. [Context Switching Awareness](#context-switching-awareness)
3. [Buffer Time Management](#buffer-time-management)
4. [ADHD-Friendly Scheduling Rules](#adhd-friendly-scheduling-rules)
5. [Break Recommendations](#break-recommendations)
6. [Flexible Planning](#flexible-planning)
7. [Hyperfocus Support](#hyperfocus-support)

## Energy Level Tracking

### Problem Statement

People with ADHD often experience fluctuating energy levels throughout the day. High-energy tasks attempted during low-energy periods lead to frustration and incomplete work.

### Solution

**Automated Energy Pattern Learning**

The system learns your natural energy rhythms and schedules tasks accordingly.

**How It Works**:

1. **Passive Tracking**
   - Monitors when you complete tasks
   - Tracks task difficulty vs. completion time
   - Identifies patterns:
     ```
     Pattern detected:
     - 9am-12pm: Complete high-energy tasks quickly
     - 2pm-4pm: Struggle with complex tasks
     - 7pm-9pm: Second wind for creative work
     ```

2. **Active Check-ins**
   - Periodic energy level prompts
   - Voluntary self-reporting
   - Quick, non-intrusive (1 click)

3. **Prediction**
   - Predicts current energy level based on:
     - Time of day
     - Recent activity
     - Historical patterns
     - Time since last break

**User Benefits**:

- **Right Task, Right Time**: High-energy tasks scheduled for peak times
- **Reduced Frustration**: Don't attempt difficult tasks when exhausted
- **Better Estimates**: System learns how long tasks *actually* take at different energy levels
- **Self-Awareness**: Visualize your energy patterns

**Implementation Details**:

```python
# Energy levels for tasks
EnergyLevel.HIGH    # Complex, creative, or cognitively demanding
EnergyLevel.MEDIUM  # Standard work tasks
EnergyLevel.LOW     # Administrative, simple, routine tasks

# Matching algorithm
def match_task_to_time(task, available_slots):
    for slot in available_slots:
        predicted_energy = predict_energy(slot.time)

        # Prefer matching or higher energy
        if predicted_energy >= task.estimated_energy_level:
            return slot  # Good match!

    # If no perfect match, warn user
    return suggest_reschedule(task)
```

**Example Interaction**:

```
Agent: "I noticed you want to work on 'Write presentation'
(HIGH energy task), but it's 3pm and you're typically
low-energy right now.

Recommendation:
- Schedule for tomorrow 9am (your peak time)
- Or break it into smaller chunks you can handle now

Which would you prefer?"
```

## Context Switching Awareness

### Problem Statement

Context switching is particularly costly for ADHD. Jumping between different types of tasks depletes mental energy and reduces productivity.

### Solution

**Minimize and Account for Context Switches**

**How It Works**:

1. **Context Detection**
   - Categorizes tasks by context:
     ```
     Contexts:
     - "work/coding"
     - "work/writing"
     - "work/meetings"
     - "personal/errands"
     - "personal/creative"
     ```

2. **Switch Counting**
   - Tracks switches in a time period
   - Warns when switching too frequently
   - Example:
     ```
     9:00-10:00  Code review (work/coding)
     10:10-11:00 Write report (work/writing)  ← Switch
     11:10-12:00 Design slides (work/creative) ← Switch
                                               ⚠️ 3 switches in 3 hours!
     ```

3. **Automatic Penalties**
   - Adds extra time after context switches
   - Default: 5-10 minute penalty
   - Adjustable based on switch severity
   - Example:
     ```
     Coding → Email = Low penalty (5 min)
     Coding → Creative = High penalty (15 min)
     ```

4. **Grouping Suggestions**
   ```
   Agent: "I see you have 3 coding tasks and 2 writing tasks.

   Instead of alternating, try:

   Morning (9am-12pm):
   - All 3 coding tasks (stay in code mindset)
   - 1 buffer break

   Afternoon (1pm-3pm):
   - Both writing tasks (stay in writing mindset)

   This avoids 4 context switches and saves ~30 minutes!"
   ```

**User Benefits**:

- **Less Mental Fatigue**: Fewer switches = more energy
- **Realistic Schedules**: Accounts for "getting back into it" time
- **Batch Processing**: Encourages grouping similar tasks
- **Awareness**: Visualize switch costs

**Implementation Details**:

```python
def calculate_context_switch_penalty(task1, task2, user_prefs):
    """Calculate extra time needed when switching contexts"""

    # No penalty if same context
    if task1.context_category == task2.context_category:
        return 0

    # Base penalty from user preferences
    base_penalty = user_prefs.context_switch_penalty  # e.g., 10 min

    # Increase for severe switches
    if is_severe_switch(task1.context_category, task2.context_category):
        return base_penalty * 1.5  # 15 min

    return base_penalty


def is_severe_switch(context1, context2):
    """Determine if switch is particularly disruptive"""

    severe_pairs = [
        ("work/coding", "work/writing"),
        ("work/analytical", "work/creative"),
        ("work/focused", "personal/social")
    ]

    return (context1, context2) in severe_pairs
```

## Buffer Time Management

### Problem Statement

ADHD minds need transition time between tasks. Jumping immediately from one task to another leads to overwhelm and incomplete transitions.

### Solution

**Automatic Buffer Time Insertion**

**How It Works**:

1. **Between Different Tasks**
   - Inserts 10-15 minute buffer by default
   - Adjustable per user preference
   - Example schedule:
     ```
     9:00-10:00   Task A
     10:00-10:10  BUFFER
     10:10-11:10  Task B
     ```

2. **After Meetings**
   - Longer buffer (15-20 min)
   - Account for context reload
   - Example:
     ```
     2:00-3:00    Team meeting
     3:00-3:20    BUFFER (decompress + reload context)
     3:20-4:20    Code review
     ```

3. **Buffer Activities**
   - Suggested uses:
     - Stretch, walk, water
     - Review notes from previous task
     - Prepare for next task
     - Quick mindfulness
   - Not empty time - intentional transition

**User Benefits**:

- **Mental Space**: Time to mentally switch gears
- **Realistic Schedules**: Account for human needs
- **Reduced Overwhelm**: Don't feel constantly rushed
- **Better Transitions**: Start next task with fresh mind

**Implementation**:

```python
def create_schedule_with_buffers(tasks, calendar_events, preferences):
    schedule = []

    for i, task in enumerate(tasks):
        # Add the task
        schedule.append(create_time_block(task))

        # Add buffer before next task (if not last task)
        if i < len(tasks) - 1:
            next_task = tasks[i + 1]

            # Determine buffer duration
            if task.block_type == "meeting":
                buffer_duration = 20  # Longer after meetings
            elif needs_context_switch(task, next_task):
                buffer_duration = preferences.buffer_time_between_tasks
            else:
                buffer_duration = 5  # Minimal for same context

            schedule.append(create_buffer_block(buffer_duration))

    return schedule
```

## ADHD-Friendly Scheduling Rules

### Problem Statement

Traditional productivity advice doesn't work for ADHD. Need specialized scheduling rules.

### Solution

**Built-in ADHD Heuristics**

**Rules**:

1. **Max Focus Duration**
   - Default: 45 minutes
   - Don't schedule tasks longer than this without breaks
   - Split long tasks into sessions
   - Example:
     ```
     ❌ Bad:
     9:00-12:00  Write report (3 hours straight)

     ✅ Good:
     9:00-9:45   Write report (Part 1)
     9:45-10:00  BREAK
     10:00-10:45 Write report (Part 2)
     10:45-11:00 BREAK
     11:00-11:45 Write report (Part 3)
     ```

2. **Energy-Task Matching**
   - HIGH energy tasks → Peak energy times
   - MEDIUM tasks → Normal times
   - LOW tasks → Low energy times
   - Never schedule HIGH tasks in LOW energy times

3. **Quick Wins First (Optional)**
   - Start day with easy task for momentum
   - Builds confidence
   - Example:
     ```
     9:00-9:15   Reply to emails (quick win!)
     9:15-10:15  Tackle hard task (momentum built)
     ```

4. **Hyperfocus Protection**
   - If user is in flow, don't interrupt
   - Defer notifications
   - Flexible time blocks

5. **Variety vs. Monotony Balance**
   - Don't schedule 4 similar tasks in a row
   - Alternate task types when possible
   - Example:
     ```
     ✅ Good variety:
     9:00-10:00  Coding
     10:10-11:00 Writing
     11:10-12:00 Coding
     12:00-1:00  LUNCH
     1:00-2:00   Meeting

     ❌ Monotonous:
     9:00-10:00  Writing
     10:10-11:00 Writing
     11:10-12:00 Writing
     12:00-1:00  LUNCH
     1:00-2:00   Writing  (brain will revolt!)
     ```

6. **Deadline Proximity Boost**
   - As deadline approaches, prioritize automatically
   - 24 hours before: Urgent priority
   - Prevent last-minute panic

**User Benefits**:

- **Sustainable Productivity**: Work with ADHD, not against it
- **Prevent Burnout**: Breaks and variety built in
- **Realistic Plans**: Account for actual ADHD brain behavior
- **Reduced Guilt**: System expects and accommodates ADHD patterns

## Break Recommendations

### Problem Statement

ADHD brains need regular breaks but often forget to take them, leading to diminishing returns and burnout.

### Solution

**Intelligent Break Suggestions**

**How It Works**:

1. **Automatic Break Scheduling**
   - After 45 min focus time
   - After meetings
   - After context switches
   - When energy drops

2. **Break Notifications**
   ```
   Agent: "You've been coding for 50 minutes. Time for a break!

   Suggestions:
   - 5 min: Stretch, water, bathroom
   - 10 min: Short walk
   - 15 min: Full mental reset

   Your next task (writing) starts in 15 minutes.

   [Start 5min break] [Start 10min break] [Skip (not recommended)]"
   ```

3. **Break Activity Suggestions**
   - **Physical**: Walk, stretch, exercise
   - **Mental**: Meditation, breathing
   - **Social**: Quick chat with colleague
   - **Creative**: Doodle, music
   - **Practical**: Snack, water, bathroom

4. **Hyperfocus Override**
   - If user is deep in flow, suggest but don't force
   - Defer notification to natural break point
   - Example:
     ```
     Agent (quietly): "I'll remind you to take a break when you
     finish this coding session. Keep going! 💪"
     ```

**User Benefits**:

- **Prevent Exhaustion**: Regular recharging
- **Better Focus**: Fresh mind for each task
- **Physical Health**: Movement prompts
- **Sustained Performance**: Avoid afternoon crashes

## Flexible Planning

### Problem Statement

Rigid schedules don't work for ADHD. Need ability to easily modify plans without guilt or penalty.

### Solution

**Forgiveness and Flexibility**

**Features**:

1. **Easy Rescheduling**
   - Drag-and-drop calendar
   - "Schedule for tomorrow" button
   - No penalties or warnings for changes

2. **Incomplete Task Handling**
   ```
   Agent: "I see you didn't finish 'Write report' today.
   No worries! Would you like to:

   1. Reschedule for tomorrow
   2. Break it into smaller pieces
   3. Cancel it (if no longer needed)

   What works best?"
   ```

3. **Flexible Time Estimates**
   - Show ranges instead of fixed times
   - "1-2 hours" instead of "90 minutes"
   - Adjust based on actual performance

4. **No Guilt Mode**
   - Positive framing: "Let's reschedule" not "You missed it"
   - Celebrate completed tasks, ignore incomplete ones
   - Focus on progress, not perfection

**User Benefits**:

- **Reduced Anxiety**: It's okay to change plans
- **Realistic Self-View**: Not failing, just adapting
- **Sustainable System**: Won't abandon due to guilt
- **Honest Planning**: Will actually use it

## Hyperfocus Support

### Problem Statement

ADHD hyperfocus is a superpower but can lead to neglecting other important tasks or self-care.

### Solution

**Hyperfocus Detection and Management**

**How It Works**:

1. **Detection**
   - Task goes beyond scheduled time
   - User hasn't responded to notifications
   - Pattern: Deep in one task for extended period

2. **Gentle Interrupts**
   ```
   Agent (after 90 min): "You've been coding for 1.5 hours!
   You're on a roll, which is great!

   Just a friendly reminder:
   - Next task (meeting) in 30 minutes
   - You might want to save your work soon
   - Maybe grab water?

   Keep crushing it! 💪

   [5 more minutes] [Wrap up now] [Dismiss]"
   ```

3. **Hyperfocus Blocks**
   - User can schedule "hyperfocus time"
   - No interruptions during these blocks
   - System protects this time
   - Example:
     ```
     9:00-12:00  HYPERFOCUS: Deep coding session
                 (No notifications, no interruptions)
     ```

4. **Post-Hyperfocus Recovery**
   - Automatic longer break after hyperfocus
   - Energy replenishment time
   - Gentle re-entry to normal schedule

**User Benefits**:

- **Harness Hyperfocus**: Use it productively
- **Prevent Negative Effects**: Don't miss important things
- **Self-Care Prompts**: Remember to eat, drink, move
- **Flexible System**: Works with ADHD strengths

## Time Blindness Mitigation

### Problem Statement

ADHD time blindness makes it hard to estimate duration and notice time passing.

### Solution

**Visual Time Awareness**

**Features**:

1. **Time Block Visualization**
   - Visual calendar shows time passing
   - Current time indicator moves
   - Upcoming tasks highlighted

2. **Time Warnings**
   ```
   Agent: "Quick heads up: You have 15 minutes left for
   'Code review'. Might be a good time to start wrapping up!"
   ```

3. **Realistic Time Estimates**
   - Learn from actual completion times
   - Adjust estimates automatically
   - Show "usually takes you X minutes"

4. **Duration Indicators**
   - Tasks show how long they'll take
   - Visual progress bars
   - "25 minutes left" countdown

**User Benefits**:

- **Better Time Sense**: External cues help awareness
- **Realistic Planning**: Learn actual task durations
- **Prevent Lateness**: Warnings before meetings
- **Reduced Anxiety**: Know where you are in time

## Related Documentation

- [UI Specifications](ui-specifications.md)
- [Workflows](workflows.md)
- [Agent System](../architecture/agent-system.md)
- [User Guide](../user/user-guide.md)
