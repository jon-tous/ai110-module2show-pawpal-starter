from datetime import datetime, date, timedelta

from pawpal_system import Owner, Pet, Task, TaskManager, Scheduler

# set up owner
owner = Owner(name="Alex", contact_info="alex@example.com", preferences={"max_minutes_per_day": 300})

# set up pets
pet1 = Pet(id="pet1", owner_id="owner1", name="Bella", species="Dog", age=4, health_notes="none", default_tasks=["walk", "feed"])
pet2 = Pet(id="pet2", owner_id="owner1", name="Milo", species="Cat", age=2, health_notes="urgent medication", default_tasks=["feed"])

# set up task manager
manager = TaskManager()
manager.owners.append(owner)
manager.pets.extend([pet1, pet2])

# set up sample tasks
now = datetime.now()
manager.add_task(Task(id="task1", title="Morning Walk", pet_id="pet1", duration=30, priority=5, due_time=now + timedelta(hours=2)))
manager.add_task(Task(id="task2", title="Give Medication", pet_id="pet2", duration=15, priority=9, due_time=now + timedelta(hours=1)))
manager.add_task(Task(id="task3", title="Evening Grooming", pet_id="pet1", duration=45, priority=3, due_time=now + timedelta(hours=3)))

# generate today's schedule
scheduler = Scheduler(constraints={"max_minutes": 180})
plan = scheduler.generate_daily_plan(manager, date.today())

# print schedule
print("Today's Schedule")
print(plan.describe())
