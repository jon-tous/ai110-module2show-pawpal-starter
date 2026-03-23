from datetime import date, datetime, timedelta

import streamlit as st

from pawpal_system import Owner, Pet, Task, TaskManager, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app
so you can start quickly, but **it does not implement the project
logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend
classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner
plan care tasks for their pet(s) based on constraints like time,
priority, and preferences.

You will design and implement the scheduling logic and connect it to
this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks
    based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

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

task_manager = st.session_state.task_manager
scheduler = st.session_state.scheduler
owner = st.session_state.owner

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
    pet_age = st.number_input("Pet age", min_value=0, max_value=40, value=2)
    health_notes = st.text_input("Health notes", value="")
    default_tasks = st.text_input(
        "Default tasks (comma separated)", value="feed, walk"
    )
    pet_submitted = st.form_submit_button("Add pet")

if pet_submitted:
    pet = Pet(
        id=f"pet-{st.session_state.pet_counter}",
        owner_id="owner-1",
        name=pet_name,
        species=species,
        age=int(pet_age),
        health_notes=health_notes or None,
        default_tasks=[
            task.strip() for task in default_tasks.split(",") if task.strip()
        ],
    )
    task_manager.add_pet(pet)
    st.session_state.pet_counter += 1
    st.success(f"Added pet: {pet.name}")
    st.rerun()

if task_manager.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "name": pet.name,
                "species": pet.species,
                "age": pet.age,
                "health_notes": pet.health_notes or "",
            }
            for pet in task_manager.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks and send them through your backend task manager.")

priority_map = {"low": 1, "medium": 2, "high": 3}

if task_manager.pets:
    with st.form("task_form"):
        selected_pet_name = st.selectbox(
            "Assign to pet",
            [pet.name for pet in task_manager.pets],
        )
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        priority_label = st.selectbox(
            "Priority", ["low", "medium", "high"], index=2
        )
        due_in_hours = st.number_input(
            "Due in hours", min_value=1, max_value=24, value=2
        )
        task_submitted = st.form_submit_button("Add task")

    if task_submitted:
        selected_pet = next(
            pet for pet in task_manager.pets if pet.name == selected_pet_name
        )
        task = Task(
            id=f"task-{st.session_state.task_counter}",
            title=task_title,
            pet_id=selected_pet.id,
            duration=int(duration),
            priority=priority_map[priority_label],
            due_time=datetime.now() + timedelta(hours=int(due_in_hours)),
        )
        task_manager.add_task(task)
        st.session_state.task_counter += 1
        st.success(f"Added task: {task.title}")
        st.rerun()
else:
    st.caption("Add a pet first so tasks can be assigned correctly.")

if task_manager.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.title,
                "pet_id": task.pet_id,
                "duration_minutes": task.duration,
                "priority": task.priority,
                "due_time": task.due_time,
                "status": task.status,
            }
            for task in task_manager.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button now calls your scheduler and displays today's plan.")

if st.button("Generate schedule"):
    plan = scheduler.generate_daily_plan(task_manager, date.today())
    st.success("Schedule generated.")
    st.text(plan.describe())

    if plan.unscheduled_tasks:
        st.write("Unscheduled tasks:")
        st.table(
            [
                {
                    "title": task.title,
                    "duration": task.duration,
                    "priority": task.priority,
                }
                for task in plan.unscheduled_tasks
            ]
        )
