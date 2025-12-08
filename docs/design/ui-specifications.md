# UI Specifications

## Overview

This document specifies the Streamlit-based user interface for ADHD Planner, including page layouts, component specifications, and user interaction patterns.

## Table of Contents
1. [Design Principles](#design-principles)
2. [Page Specifications](#page-specifications)
3. [Component Library](#component-library)
4. [Navigation](#navigation)
5. [Responsive Design](#responsive-design)

## Design Principles

### ADHD-First Design

- **Low Friction**: Minimal clicks, natural language input
- **Visual Clarity**: Clear status indicators, color coding
- **Flexibility**: Easy to modify, reschedule, or cancel
- **Forgiveness**: No penalties for changing plans
- **Immediate Feedback**: Instant response to actions

### Visual Design

- **Clean Layout**: Uncluttered, focused design
- **Consistent Patterns**: Same interactions throughout
- **Visual Hierarchy**: Important information stands out
- **Color Coding**:
  - High energy: Red/Orange
  - Medium energy: Yellow
  - Low energy: Green/Blue
  - Synced: Blue checkmark
  - Pending sync: Orange clock
  - Error: Red exclamation

## Page Specifications

### Chat Page

**Purpose**: Conversational interface with AI agents

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│  ADHD Planner - Chat                          [⚙️]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Conversation History]                             │
│                                                     │
│  User: Add task to write report                     │
│  Agent: I'll help you add that task. How long       │
│         do you think it will take?                  │
│  User: Maybe 2 hours?                               │
│  Agent: Got it! I've created the task "Write        │
│         report" with 2h estimate. Based on your     │
│         energy patterns, I suggest scheduling       │
│         this for tomorrow morning at 9am when       │
│         you're usually most focused. Sound good?    │
│                                                     │
│  [Suggested Actions]                                │
│  [✓ Schedule it] [~ Show alternatives] [✏️ Modify] │
│                                                     │
├─────────────────────────────────────────────────────┤
│  💬 Your message: ____________  [Send] or [Enter]   │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Message history with clear User/Agent distinction
- Suggested quick actions from agent
- Input field with send button and keyboard shortcut
- Auto-scroll to latest message
- Typing indicator when agent is thinking
- Markdown support for formatted responses

**Components**:
- `ChatMessage` - Individual message component
- `QuickActionButton` - Suggested action buttons
- `ChatInput` - Message input field
- `TypingIndicator` - Loading animation

### Calendar View

**Purpose**: Visual time blocking and scheduling

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│  ADHD Planner - Calendar         [Week▾] [Day▾] [⚙️]│
├─────────────────────────────────────────────────────┤
│  ◀ Mon 1/13   Tue 1/14   Wed 1/15   Thu 1/16 ▶     │
│                                                     │
│  9:00  ┌──────────┐  ┌──────────┐                  │
│        │ Write    │  │ Meeting  │                  │
│        │ report   │  │          │                  │
│  10:00 │ [🔴HIGH] │  └──────────┘                  │
│        └──────────┘                                 │
│  11:00    [BUFFER]   ┌──────────┐                  │
│                      │ Code     │                  │
│  12:00               │ review   │                  │
│                      │ [🟡MED]  │                  │
│                      └──────────┘                  │
│  13:00  [LUNCH BREAK]                              │
│                                                     │
│  Energy: ████████░░░░░ (High morning → Low afternoon)│
│                                                     │
│  [+ Add Block] [🔄 Sync Now] [💡 Suggestions]       │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Week/Day toggle view
- Color-coded time blocks by energy level
- Drag-and-drop rescheduling
- Visual energy level indicator
- Sync status per block
- Click to edit block details
- Auto-scroll to current time
- Visual differentiation of block types (task/break/buffer)

**Components**:
- `TimeBlock` - Individual calendar block
- `TimeGrid` - Calendar grid layout
- `EnergyMeter` - Energy level visualization
- `TimeBlockModal` - Edit block dialog

### Tasks Page

**Purpose**: Comprehensive task list and management

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│  ADHD Planner - Tasks                          [⚙️]  │
├─────────────────────────────────────────────────────┤
│  🔍 Search: _______  [Filter: All ▾] [Sort: Priority ▾] │
│  [+ New Task]                                       │
│                                                     │
│  TODAY (2)                                          │
│  ┌───────────────────────────────────────────────┐ │
│  │ ☐ Write report [2h] [🔴HIGH] 🔄Synced        │ │
│  │   Due: Today 5pm                               │ │
│  │   [Schedule] [Edit] [Delete]                   │ │
│  └───────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────┐ │
│  │ ☐ Code review [1h] [🟡MED] 🔄Synced          │ │
│  │   Due: Tomorrow                                │ │
│  │   [Schedule] [Edit] [Delete]                   │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  UPCOMING (3)                                       │
│  ┌───────────────────────────────────────────────┐ │
│  │ ☐ Plan presentation [3h] [🔴HIGH]            │ │
│  │   Due: Jan 15 | Sync: [Toggle OFF]            │ │
│  │   [Schedule] [Edit] [Delete]                   │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ✓ COMPLETED (5) [Show/Hide]                       │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Search and filter tasks
- Sort by multiple criteria
- Quick task creation
- Per-item sync toggle
- Batch operations
- Expandable sections (Today/Upcoming/Completed)
- Task detail modal
- Energy and priority badges
- Sync status indicators

**Components**:
- `TaskCard` - Individual task display
- `TaskModal` - Task create/edit form
- `TaskFilters` - Search and filter controls
- `SyncToggle` - Per-task sync control

### Settings Page

**Purpose**: User preferences and configuration

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│  ADHD Planner - Settings                       [⚙️]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📱 LLM CONFIGURATION                               │
│  Provider: [Ollama ▾]                               │
│  Model: [llama3.1 ▾]                                │
│  Temperature: [0.7] ═════════                       │
│  [Test Connection]                                  │
│                                                     │
│  ⏰ WORK PREFERENCES                                │
│  Work hours: [9:00] to [17:00]                      │
│  Max focus time: [45] minutes                       │
│  Break duration: [15] minutes                       │
│  Buffer between tasks: [10] minutes                 │
│                                                     │
│  ⚡ ENERGY PATTERNS                                 │
│  Peak energy: [9am-12pm] [× Remove] [+ Add]         │
│  Low energy: [2pm-4pm] [× Remove] [+ Add]           │
│                                                     │
│  🔄 SYNC SETTINGS                                   │
│  ☑ Enable Apple Reminders sync                     │
│  ☑ Enable Apple Calendar sync                      │
│  Sync interval: [5] minutes                         │
│  Default sync new tasks: [Yes ▾]                    │
│  Last sync: 2 minutes ago | [Sync Now]              │
│                                                     │
│  💾 DATA MANAGEMENT                                 │
│  [Export Tasks] [Import Tasks] [Backup Database]    │
│                                                     │
│  [Save Settings] [Reset to Defaults]                │
└─────────────────────────────────────────────────────┘
```

**Features**:
- LLM provider configuration with testing
- Work preference customization
- Energy pattern management
- Sync configuration
- Data export/import
- Real-time validation
- Save confirmation

**Components**:
- `ProviderSelector` - LLM provider dropdown
- `TimeRangePicker` - Energy time range selector
- `SliderInput` - Numeric sliders
- `ToggleSwitch` - Boolean settings

## Component Library

### TaskCard

**Purpose**: Display task summary with key information

**Anatomy**:
```
┌─────────────────────────────────────────────────┐
│ [Checkbox] Task Title                      [⋮]  │
│ 📝 Description preview...                       │
│ ⏱ 2h | 🔴HIGH | 📅 Due: Jan 15 | 🔄Synced      │
│ #tag1 #tag2                                     │
└─────────────────────────────────────────────────┘
```

**Props**:
- `task: Task` - Task data
- `on_toggle: () => void` - Complete/uncomplete handler
- `on_edit: () => void` - Edit handler
- `on_delete: () => void` - Delete handler

**States**:
- Default
- Hover (show actions)
- Completed (strikethrough, muted)
- Overdue (red border)

### TimeBlock Component

**Purpose**: Visual representation of scheduled time

**Anatomy**:
```
┌──────────────┐
│ Task Title   │ ← Task name or block type
│ 2h | 🔴HIGH  │ ← Duration and energy
│ 🔄Synced     │ ← Sync status
└──────────────┘
```

**Props**:
- `time_block: TimeBlock` - Block data
- `task: Optional[Task]` - Associated task
- `on_click: () => void` - Edit handler
- `draggable: bool` - Enable drag-and-drop

**States**:
- Default
- Hover (highlight)
- Dragging (semi-transparent)
- Past (muted)
- Current (highlighted border)

### EnergyMeter Component

**Purpose**: Visualize energy level

**Display**:
```
Energy: ████████░░░░░ 65% (Medium-High)
```

**Props**:
- `level: EnergyLevel | float` - Energy level
- `show_label: bool` - Display text label
- `compact: bool` - Compact view

**Variants**:
- Bar graph (default)
- Circle indicator
- Text only
- Icon only (⚡ color-coded)

### SyncStatus Indicator

**Purpose**: Show sync status

**Display**:
```
🔄Synced          ← Successfully synced
⏳Pending         ← Queued for sync
❌Error          ← Sync failed
🚫Disabled        ← Sync disabled
⚠️Conflict        ← Needs resolution
```

**Props**:
- `status: SyncStatus` - Current status
- `last_synced: datetime` - Last sync time
- `on_sync: () => void` - Manual sync handler

## Navigation

### Main Navigation

**Location**: Sidebar or top bar

**Structure**:
```
┌─────────────────┐
│ ADHD Planner    │
├─────────────────┤
│ 💬 Chat         │ ← Default page
│ 📅 Calendar     │
│ ✓ Tasks         │
│ ⚙️ Settings     │
├─────────────────┤
│ Current Energy: │
│ ███████░░ High  │
│                 │
│ Next: Meeting   │
│ in 30 min       │
└─────────────────┘
```

**Features**:
- Active page highlight
- Energy status widget
- Upcoming event preview
- Quick access to all pages

### Breadcrumbs

For modal dialogs and deep navigation:
```
Tasks > Edit Task > "Write Report"
```

## Responsive Design

### Breakpoints

- **Desktop**: > 1024px (full layout)
- **Tablet**: 768-1024px (compact sidebar)
- **Mobile**: < 768px (bottom nav, stacked layout)

### Mobile Adaptations

**Chat Page**:
- Full-screen message view
- Floating action button for input
- Swipe to access quick actions

**Calendar View**:
- Day view only (no week view)
- Swipe to change days
- Tap to edit blocks

**Tasks Page**:
- Card-based layout
- Swipe actions (complete/delete)
- Floating + button for new task

**Settings Page**:
- Accordion sections
- Full-width inputs
- Sticky save button

## Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: ARIA labels on all interactive elements
- **Color Contrast**: WCAG AA compliance
- **Focus Indicators**: Clear focus states
- **Alt Text**: Images and icons have descriptions

## Interaction Patterns

### Drag-and-Drop (Calendar)

```
1. User clicks time block
2. Block highlights
3. User drags to new time slot
4. Valid slots highlight in green
5. Invalid slots show red
6. Drop to move
7. Confirm dialog if sync enabled
```

### Task Creation

```
1. User types in chat: "Add task: X"
   OR clicks "+ New Task" button
2. Agent/form extracts details
3. Preview shown with suggestions
4. User confirms or modifies
5. Task created
6. Sync queued if enabled
7. Confirmation message
```

### Sync Triggering

```
1. Automatic (periodic): Every N minutes
2. Manual: Click "Sync Now" button
3. On-change (debounced): After modification
4. On-demand: Before viewing calendar
```

## Theme & Styling

### Color Palette

**Primary Colors**:
- Brand: `#6366f1` (Indigo)
- Success: `#10b981` (Green)
- Warning: `#f59e0b` (Amber)
- Error: `#ef4444` (Red)

**Energy Colors**:
- High: `#ef4444` (Red)
- Medium: `#f59e0b` (Amber)
- Low: `#3b82f6` (Blue)

**Background**:
- Primary: `#ffffff` (White)
- Secondary: `#f3f4f6` (Gray-100)
- Tertiary: `#e5e7eb` (Gray-200)

**Text**:
- Primary: `#1f2937` (Gray-800)
- Secondary: `#6b7280` (Gray-500)
- Muted: `#9ca3af` (Gray-400)

### Typography

- **Headings**: Inter, sans-serif, 600 weight
- **Body**: Inter, sans-serif, 400 weight
- **Monospace**: JetBrains Mono (for IDs, technical info)

### Spacing

- **Unit**: 8px base
- **Compact**: 4px (0.5 units)
- **Normal**: 8px (1 unit)
- **Comfortable**: 16px (2 units)
- **Spacious**: 24px (3 units)

## Related Documentation

- [Workflows](workflows.md)
- [ADHD Features](adhd-features.md)
- [Component Implementation](../technical/directory-structure.md#ui-layer)
