from datetime import date, datetime, timedelta

import streamlit as st

from pawpal_system import Owner, Pet, Task, TaskManager, Scheduler


def format_due_time(task_due_time: datetime | None) -> str:
    if task_due_time is None:
        return "No due time"
    return task_due_time.strftime("%Y-%m-%d %H:%M")


def build_pet_lookup(manager: TaskManager) -> dict[str, str]:
    return {pet.id: pet.name for pet in manager.pets}


def task_rows(
    tasks: list[Task],
    manager: TaskManager,
) -> list[dict[str, str]]:
    pet_lookup = build_pet_lookup(manager)
    rows = []
    for item in tasks:
        rows.append(
            {
                "Task": item.title,
                "Pet": pet_lookup.get(item.pet_id, item.pet_id),
                "Duration (min)": item.duration,
                "Priority": item.priority,
                "Due": format_due_time(item.due_time),
                "Recurrence": item.recurrence or "one-time",
                "Status": item.status,
            }
        )
    return rows


def schedule_rows(plan_obj, manager: TaskManager) -> list[dict[str, str]]:
    pet_lookup = build_pet_lookup(manager)
    rows = []
    for slot in plan_obj.slots:
        rows.append(
            {
                "Task": slot.task.title,
                "Pet": pet_lookup.get(slot.task.pet_id, slot.task.pet_id),
                "Start": slot.start_time.strftime("%H:%M"),
                "End": slot.end_time.strftime("%H:%M"),
                "Duration (min)": slot.duration(),
                "Priority": slot.task.priority,
            }
        )
    return rows


def task_option_label(item: Task, manager: TaskManager) -> str:
    pet_lookup = build_pet_lookup(manager)
    pet_label = pet_lookup.get(item.pet_id, item.pet_id)
    return (
        f"{item.title} - {pet_label} - "
        f"{format_due_time(item.due_time)}"
    )


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")
st.caption(
    "Plan pet care with smart scheduling, recurrence handling, "
    "and clear conflict alerts."
)

if "task_manager" not in st.session_state:
    st.session_state.task_manager = TaskManager()

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(constraints={"max_minutes": 240})

if "owner" not in st.session_state:
    default_owner = Owner(name="Jordan")
    st.session_state.owner = default_owner
    st.session_state.task_manager.add_owner(default_owner)

if "pet_counter" not in st.session_state:
    st.session_state.pet_counter = 1

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 1

if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = None

task_manager = st.session_state.task_manager
scheduler = st.session_state.scheduler
owner = st.session_state.owner

with st.expander("How this planner works", expanded=False):
    st.markdown(
        """
The UI now uses the backend scheduler directly:
- task lists can be filtered and sorted chronologically
- recurring tasks can create the next task automatically when completed
- daily schedules surface conflicts as warnings instead of hiding them
"""
    )

setup_col, tasks_col = st.columns([1, 1.2])

with setup_col:
    st.subheader("Owner + Pet Setup")

    with st.form("owner_form"):
        owner_name = st.text_input("Owner name", value=owner.name)
        max_minutes = st.number_input(
            "Max daily task minutes",
            min_value=30,
            max_value=720,
            value=int(owner.preferences.get("max_minutes_per_day", 240)),
            step=15,
        )
        owner_submitted = st.form_submit_button("Save owner preferences")

    if owner_submitted:
        owner.name = owner_name
        owner.update_preferences({"max_minutes_per_day": int(max_minutes)})
        scheduler.constraints["max_minutes"] = int(max_minutes)
        st.success("Owner preferences saved.")

    with st.form("pet_form"):
        pet_name = st.text_input("Pet name", value="Mochi")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        pet_age = st.number_input(
            "Pet age",
            min_value=0,
            max_value=40,
            value=2,
        )
        health_notes = st.text_input("Health notes", value="")
        default_tasks = st.text_input(
            "Default tasks (comma separated)",
            value="feed, walk",
        )
        pet_submitted = st.form_submit_button("Add pet")

    if pet_submitted:
        try:
            pet = Pet(
                id=f"pet-{st.session_state.pet_counter}",
                owner_id="owner-1",
                name=pet_name,
                species=species,
                age=int(pet_age),
                health_notes=health_notes or None,
                default_tasks=[
                    task.strip()
                    for task in default_tasks.split(",")
                    if task.strip()
                ],
            )
            task_manager.add_pet(pet)
            st.session_state.pet_counter += 1
            st.success(f"Added pet: {pet.name}")
            st.rerun()
        except ValueError as exc:
            st.warning(str(exc))

    if task_manager.pets:
        st.table(
            [
                {
                    "Name": pet.name,
                    "Species": pet.species,
                    "Age": pet.age,
                    "Health notes": pet.health_notes or "",
                }
                for pet in task_manager.pets
            ]
        )
    else:
        st.info("No pets yet. Add one above.")

with tasks_col:
    st.subheader("Tasks")

    priority_map = {"low": 1, "medium": 2, "high": 3}
    recurrence_map = {
        "One-time": None,
        "Daily": "daily",
        "Weekly": "weekly",
    }

    if task_manager.pets:
        with st.form("task_form"):
            selected_pet_name = st.selectbox(
                "Assign to pet",
                [pet.name for pet in task_manager.pets],
            )
            task_title = st.text_input("Task title", value="Morning walk")
            duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=240,
                value=20,
            )
            priority_label = st.selectbox(
                "Priority",
                ["low", "medium", "high"],
                index=2,
            )
            due_in_hours = st.number_input(
                "Due in hours",
                min_value=0,
                max_value=72,
                value=2,
            )
            recurrence_label = st.selectbox(
                "Recurrence",
                list(recurrence_map.keys()),
            )
            task_submitted = st.form_submit_button("Add task")

        if task_submitted:
            selected_pet = next(
                pet
                for pet in task_manager.pets
                if pet.name == selected_pet_name
            )
            due_time = None
            if int(due_in_hours) > 0:
                due_time = datetime.now() + timedelta(hours=int(due_in_hours))

            try:
                task = Task(
                    id=f"task-{st.session_state.task_counter}",
                    title=task_title,
                    pet_id=selected_pet.id,
                    duration=int(duration),
                    priority=priority_map[priority_label],
                    due_time=due_time,
                    recurrence=recurrence_map[recurrence_label],
                )
                task_manager.add_task(task)
                st.session_state.task_counter += 1
                st.success(f"Added task: {task.title}")
                st.rerun()
            except ValueError as exc:
                st.warning(str(exc))
    else:
        st.info("Add a pet first so tasks can be assigned correctly.")

    if task_manager.tasks:
        filter_col, pet_filter_col = st.columns(2)
        with filter_col:
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "pending", "completed"],
            )
        with pet_filter_col:
            pet_filter = st.selectbox(
                "Filter by pet",
                ["All pets"] + [pet.name for pet in task_manager.pets],
            )

        filtered_tasks = scheduler.filter_tasks(
            task_manager,
            status=None if status_filter == "All" else status_filter,
            pet_name=None if pet_filter == "All pets" else pet_filter,
        )

        time_sorted_tasks = scheduler.sort_tasks_by_time(filtered_tasks)
        ranked_tasks = scheduler.rank_tasks(filtered_tasks)

        st.markdown("#### Task views")
        chronological_tab, ranked_tab = st.tabs(
            ["Chronological", "Priority-ranked"]
        )

        with chronological_tab:
            st.caption(
                "Tasks are shown in due-time order using the scheduler."
            )
            st.table(task_rows(time_sorted_tasks, task_manager))

        with ranked_tab:
            st.caption(
                "Tasks are ranked by priority plus urgency using the "
                "scheduler."
            )
            st.table(task_rows(ranked_tasks, task_manager))

        pending_tasks = scheduler.filter_tasks(task_manager, status="pending")
        if pending_tasks:
            selected_task_label = st.selectbox(
                "Mark a task complete",
                [
                    task_option_label(task, task_manager)
                    for task in pending_tasks
                ],
            )
            if st.button("Complete selected task"):
                selected_task = next(
                    task
                    for task in pending_tasks
                    if task_option_label(task, task_manager)
                    == selected_task_label
                )
                new_task = scheduler.complete_task(
                    task_manager,
                    selected_task.id,
                )
                if new_task is not None:
                    st.success(
                        "Task completed. Next recurring task created for "
                        f"{format_due_time(new_task.due_time)}."
                    )
                else:
                    st.success("Task marked as completed.")
                st.rerun()
    else:
        st.info("No tasks yet. Add one above.")

st.divider()
st.subheader("Build Schedule")

schedule_date = st.date_input("Schedule date", value=date.today())
if st.button("Generate schedule"):
    st.session_state.generated_plan = scheduler.generate_daily_plan(
        task_manager,
        schedule_date,
    )

plan = st.session_state.generated_plan
if plan is not None:
    st.success(f"Schedule generated for {plan.date.isoformat()}.")

    summary_col, duration_col = st.columns(2)
    with summary_col:
        st.metric("Scheduled tasks", len(plan.slots))
    with duration_col:
        st.metric("Planned minutes", plan.total_duration)

    if plan.warnings:
        st.markdown("#### Scheduling warnings")
        for warning in plan.warnings:
            st.warning(
                f"Conflict detected: {warning} Review due times or adjust "
                "task priorities before relying on this plan."
            )

    if plan.slots:
        st.markdown("#### Planned schedule")
        st.table(schedule_rows(plan, task_manager))
    else:
        st.info("No tasks were scheduled for this date.")

    if plan.unscheduled_tasks:
        st.markdown("#### Unscheduled tasks")
        st.warning(
            "Some tasks could not fit within the available daily minutes."
        )
        st.table(task_rows(plan.unscheduled_tasks, task_manager))

    if plan.reasoning:
        st.info(f"Scheduler reasoning: {plan.reasoning}")
