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
