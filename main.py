from datetime import datetime, date, timedelta

from pawpal_system import Owner, Pet, Task, TaskManager, Scheduler


def print_task_list(title, tasks):
    print(title)
    for task in tasks:
        due_time = (
            task.due_time.strftime("%H:%M")
            if task.due_time
            else "No due time"
        )
        print(
            f"- {task.title} | pet_id={task.pet_id} | status={task.status} | "
            f"due={due_time}"
        )
    print()


# set up owner
owner = Owner(
    name="Alex",
    contact_info="alex@example.com",
    preferences={"max_minutes_per_day": 300},
)

# set up pets
pet1 = Pet(
    id="pet1",
    owner_id="owner1",
    name="Bella",
    species="Dog",
    age=4,
    health_notes="none",
    default_tasks=["walk", "feed"],
)
pet2 = Pet(
    id="pet2",
    owner_id="owner1",
    name="Milo",
    species="Cat",
    age=2,
    health_notes="urgent medication",
    default_tasks=["feed"],
)

# set up task manager
manager = TaskManager()
manager.add_owner(owner)
manager.add_pet(pet1)
manager.add_pet(pet2)

# set up sample tasks
now = datetime.now()
manager.add_task(
    Task(
        id="task3",
        title="Evening Grooming",
        pet_id="pet1",
        duration=45,
        priority=3,
        due_time=now + timedelta(hours=3),
    )
)
manager.add_task(
    Task(
        id="task1",
        title="Morning Walk",
        pet_id="pet1",
        duration=30,
        priority=5,
        due_time=now + timedelta(hours=2),
    )
)
manager.add_task(
    Task(
        id="task5",
        title="Breakfast",
        pet_id="pet2",
        duration=10,
        priority=6,
        due_time=now + timedelta(hours=2),
    )
)
manager.add_task(
    Task(
        id="task2",
        title="Give Medication",
        pet_id="pet2",
        duration=15,
        priority=9,
        due_time=now + timedelta(hours=1),
        status="completed",
    )
)
manager.add_task(
    Task(
        id="task4",
        title="Refill Water Bowl",
        pet_id="pet2",
        duration=5,
        priority=4,
    )
)

scheduler = Scheduler(constraints={"max_minutes": 180})

sorted_tasks = scheduler.sort_tasks_by_time(manager.tasks)
pending_bella_tasks = scheduler.filter_tasks(
    manager,
    status="pending",
    pet_name="Bella",
)
completed_tasks = scheduler.filter_tasks(manager, status="completed")

print_task_list("Tasks sorted by due time:", sorted_tasks)
print_task_list("Pending tasks for Bella:", pending_bella_tasks)
print_task_list("Completed tasks:", completed_tasks)

# generate today's schedule
plan = scheduler.generate_daily_plan(manager, date.today())

# print schedule
print("Today's Schedule")
print(plan.describe())

if plan.warnings:
    print("Conflict warnings:")
    for warning in plan.warnings:
        print(f"- {warning}")
