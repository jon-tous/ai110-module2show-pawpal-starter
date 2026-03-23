# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

### Task scoring
Each task is assigned an **effective score** by `Task.effective_score()`: `priority × 10` plus an urgency bonus. The bonus increases linearly as the due time falls within the next two hours (max +2.0 points), so tasks that are both high-priority and time-sensitive naturally surface first.

### Priority-ranked ordering
`Scheduler.rank_tasks()` sorts tasks by descending effective score. Ties are broken by whether a task has a due time (dated tasks come before undated ones), then by ascending due time so the earliest deadline wins.

### Chronological ordering
`Scheduler.sort_tasks_by_time()` is a separate view that puts due time first, relegating undated tasks to the end. Used in the UI's Chronological tab so owners can scan tasks in time order regardless of priority.

### Daily schedule generation
`Scheduler.generate_daily_plan()` queries tasks due on the target date via `TaskManager.get_tasks_by_day()`. If none match that date, it falls back to all pending tasks so the planner always produces a usable plan.

### Sequential time-slot packing
`Scheduler.fit_tasks_into_slots()` assigns tasks to sequential 1-minute-resolution slots starting at 08:00, consuming up to a configurable `max_minutes` budget (default 480). Tasks that would exceed the budget are moved to `DailySchedule.unscheduled_tasks` rather than silently dropped.

### Conflict detection
`Scheduler.detect_time_conflicts()` groups tasks by exact due timestamp. Any group with two or more tasks produces a plain-English warning attached to the plan via `DailySchedule.add_warning()`. Warnings are non-fatal — the schedule is still returned and displayed.

### Recurring task automation
`Task.next_occurrence_time()` computes the next due time by adding one day (`daily`) or seven days (`weekly`) to the original due time, or to `completed_at` if the task had no due time. `Scheduler.complete_task()` marks the task done, calls `next_occurrence_time`, and adds the new instance to the manager with a collision-safe id (`-r1`, `-r2`, …).

### Status and pet filtering
`Scheduler.filter_tasks()` accepts an optional `status` string and an optional `pet_name` string (case-insensitive). Either, both, or neither can be supplied. Used by the UI to power the filter dropdowns without duplicating logic in the view layer.

## Smarter Scheduling

The scheduler includes several intelligent features to optimize pet care planning:

- **Unified Task Ordering**: Tasks are ranked by effective score (priority + urgency), with due-time tie-breaking to surface time-sensitive tasks first.
- **Flexible Filtering**: Filter tasks by completion status, pet name, or both for focused views.
- **Recurring Task Automation**: Daily and weekly tasks automatically create the next occurrence when marked complete, ensuring consistent care routines.
- **Conflict Detection**: The scheduler detects when multiple tasks are scheduled at the same time and warns the owner without crashing, allowing for manual resolution.
- **Non-Fatal Warnings**: Scheduling issues surface as warnings attached to the plan, keeping the app functional while alerting users to conflicts or constraints.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

Run the automated test suite with:

```bash
python -m pytest
```

The tests cover the core scheduler behaviors, including task sorting in chronological order, max-minutes scheduling limits, recurring daily and weekly task creation, task filtering, conflict detection for duplicate due times, and task manager CRUD behavior.

Confidence Level: 4/5 stars

This rating reflects that the full test suite is passing and covers the most important planning behaviors and edge cases, while the overall reliability still depends on broader UI integration and real-world usage patterns that are not fully exercised by the current tests.
