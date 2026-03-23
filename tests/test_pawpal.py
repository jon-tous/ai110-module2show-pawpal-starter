import pytest
from datetime import datetime, date, timedelta

from pawpal_system import Owner, Pet, Task, TaskManager, Scheduler, DailySchedule


def test_owner_preferences_and_constraints():
    owner = Owner(name="Alex")
    owner.update_preferences({"max_minutes_per_day": 180})
    owner.set_availability([{"start": "08:00", "end": "20:00"}])

    constraints = owner.get_daily_constraints(date.today())
    assert constraints["max_minutes"] == 180
    assert constraints["available_hours"] == [{"start": "08:00", "end": "20:00"}]


def test_pet_profile_priority():
    pet = Pet(id="pet1", owner_id="owner1", name="Milo", species="Cat", age=2, health_notes="urgent medication")
    assert pet.is_high_priority()
    pet.update_profile(age=3, health_notes="normal")
    assert pet.age == 3
    assert not pet.is_high_priority()


def test_task_lifecycle_properties():
    due = datetime.now() + timedelta(hours=1)
    task = Task(id="task1", title="Feed", pet_id="pet1", duration=20, priority=5, due_time=due)

    assert task.status == "pending"
    task.mark_completed()
    assert task.status == "completed"

    task.reschedule(datetime.now() + timedelta(hours=2))
    assert task.scheduled_date == task.due_time.date()

    assert not task.is_overdue(reference=datetime.now() - timedelta(hours=1))


def test_task_completion_changes_status():
    task = Task(id="task-complete", title="Brush", pet_id="pet1", duration=10, priority=1)
    assert task.status == "pending"
    task.mark_completed()
    assert task.status == "completed"


def test_task_addition_increases_pet_task_count():
    manager = TaskManager()
    task_a = Task(id="task-a", title="Feed", pet_id="pet1", duration=10, priority=2)
    task_b = Task(id="task-b", title="Walk", pet_id="pet1", duration=20, priority=3)
    assert len(manager.get_tasks_by_pet("pet1")) == 0
    manager.add_task(task_a)
    manager.add_task(task_b)
    assert len(manager.get_tasks_by_pet("pet1")) == 2


def test_task_effective_score_increases_with_urgency():
    now = datetime.now()
    task_far = Task(id="task_far", title="Far", pet_id="pet1", duration=15, priority=5, due_time=now + timedelta(hours=10))
    task_near = Task(id="task_near", title="Near", pet_id="pet1", duration=15, priority=5, due_time=now + timedelta(minutes=30))

    score_far = task_far.effective_score(now=now)
    score_near = task_near.effective_score(now=now)
    assert score_near > score_far


def test_task_manager_crud_and_queries():
    manager = TaskManager()
    task1 = Task(id="t1", title="A", pet_id="pet1", duration=10, priority=1, due_time=datetime.now())
    task2 = Task(id="t2", title="B", pet_id="pet1", duration=20, priority=2, due_time=datetime.now())

    manager.add_task(task1)
    manager.add_task(task2)

    with pytest.raises(ValueError):
        manager.add_task(task1)

    assert len(manager.get_tasks_by_pet("pet1")) == 2

    manager.edit_task("t1", title="A updated")
    assert manager.tasks[0].title == "A updated"

    manager.delete_task("t2")
    assert len(manager.tasks) == 1

    target_date = date.today()
    manager.tasks[0].scheduled_date = target_date
    assert manager.get_tasks_by_day(target_date)[0].id == "t1"


def test_scheduler_plans_today_and_respects_max_minutes():
    manager = TaskManager()
    now = datetime.now()
    manager.add_task(Task(id="t1", title="Walk", pet_id="pet1", duration=60, priority=5, due_time=now + timedelta(hours=1)))
    manager.add_task(Task(id="t2", title="Feed", pet_id="pet1", duration=60, priority=4, due_time=now + timedelta(hours=2)))
    manager.add_task(Task(id="t3", title="Groom", pet_id="pet1", duration=90, priority=3, due_time=now + timedelta(hours=3)))

    scheduler = Scheduler(constraints={"max_minutes": 120})
    plan = scheduler.generate_daily_plan(manager, date.today())

    assert isinstance(plan, DailySchedule)
    assert len(plan.slots) == 2
    assert any(slot.task.id == "t1" for slot in plan.slots)
    assert any(slot.task.id == "t2" for slot in plan.slots)
    assert any(task.id == "t3" for task in plan.unscheduled_tasks)


def test_scheduler_sort_tasks_by_time_places_undated_tasks_last():
    scheduler = Scheduler()
    now = datetime.now()
    tasks = [
        Task(
            id="t3",
            title="Anytime enrichment",
            pet_id="pet1",
            duration=15,
            priority=1,
        ),
        Task(
            id="t2",
            title="Medication",
            pet_id="pet1",
            duration=10,
            priority=3,
            due_time=now + timedelta(hours=1),
        ),
        Task(
            id="t1",
            title="Breakfast",
            pet_id="pet1",
            duration=20,
            priority=2,
            due_time=now + timedelta(minutes=30),
        ),
    ]

    sorted_tasks = scheduler.sort_tasks_by_time(tasks)

    assert [task.id for task in sorted_tasks] == ["t1", "t2", "t3"]


def test_scheduler_filter_tasks_by_status_and_pet_name():
    manager = TaskManager()
    manager.add_pet(
        Pet(
            id="pet1",
            owner_id="owner1",
            name="Bella",
            species="Dog",
            age=4,
        )
    )
    manager.add_pet(
        Pet(
            id="pet2",
            owner_id="owner1",
            name="Milo",
            species="Cat",
            age=2,
        )
    )

    completed_task = Task(
        id="t1",
        title="Morning Walk",
        pet_id="pet1",
        duration=30,
        priority=3,
        status="completed",
    )
    pending_task = Task(
        id="t2",
        title="Dinner",
        pet_id="pet1",
        duration=15,
        priority=2,
    )
    other_pet_task = Task(
        id="t3",
        title="Medication",
        pet_id="pet2",
        duration=10,
        priority=5,
    )

    manager.add_task(completed_task)
    manager.add_task(pending_task)
    manager.add_task(other_pet_task)

    scheduler = Scheduler()

    completed_for_bella = scheduler.filter_tasks(
        manager,
        status="completed",
        pet_name="Bella",
    )
    pending_for_bella = scheduler.filter_tasks(
        manager,
        status="pending",
        pet_name="bella",
    )

    assert [task.id for task in completed_for_bella] == ["t1"]
    assert [task.id for task in pending_for_bella] == ["t2"]


def test_scheduler_complete_task_creates_next_daily_occurrence():
    manager = TaskManager()
    scheduler = Scheduler()
    due_time = datetime(2026, 3, 22, 9, 0)
    recurring_task = Task(
        id="daily-walk",
        title="Daily Walk",
        pet_id="pet1",
        duration=30,
        priority=4,
        due_time=due_time,
        recurrence="daily",
    )
    manager.add_task(recurring_task)

    new_task = scheduler.complete_task(
        manager,
        "daily-walk",
        completed_at=datetime(2026, 3, 22, 9, 15),
    )

    assert recurring_task.status == "completed"
    assert new_task is not None
    assert new_task.id == "daily-walk-r1"
    assert new_task.status == "pending"
    assert new_task.recurrence == "daily"
    assert new_task.due_time == datetime(2026, 3, 23, 9, 0)


def test_scheduler_complete_task_creates_next_weekly_occurrence():
    manager = TaskManager()
    scheduler = Scheduler()
    recurring_task = Task(
        id="weekly-groom",
        title="Weekly Grooming",
        pet_id="pet1",
        duration=45,
        priority=3,
        due_time=datetime(2026, 3, 22, 18, 0),
        recurrence="weekly",
    )
    manager.add_task(recurring_task)

    new_task = scheduler.complete_task(
        manager,
        "weekly-groom",
        completed_at=datetime(2026, 3, 22, 18, 30),
    )

    assert new_task is not None
    assert new_task.id == "weekly-groom-r1"
    assert new_task.due_time == datetime(2026, 3, 29, 18, 0)
    assert new_task.scheduled_date == date(2026, 3, 29)


def test_scheduler_complete_task_does_not_clone_non_recurring_task():
    manager = TaskManager()
    scheduler = Scheduler()
    one_time_task = Task(
        id="one-time-feed",
        title="Feed",
        pet_id="pet1",
        duration=15,
        priority=2,
    )
    manager.add_task(one_time_task)

    new_task = scheduler.complete_task(manager, "one-time-feed")

    assert one_time_task.status == "completed"
    assert new_task is None
    assert len(manager.tasks) == 1
