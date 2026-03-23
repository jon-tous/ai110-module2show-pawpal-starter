from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any


@dataclass
class Owner:
    name: str
    contact_info: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    available_hours: List[Dict[str, Any]] = field(default_factory=list)

    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update the owner's stored scheduling preferences."""
        self.preferences.update(preferences)

    def set_availability(self, availability: List[Dict[str, Any]]) -> None:
        """Set the owner's available hours for planning."""
        self.available_hours = availability

    def get_daily_constraints(self, _target_date: date) -> Dict[str, Any]:
        """Return the owner's planning constraints for a given day."""
        return {
            "available_hours": self.available_hours,
            "max_minutes": self.preferences.get("max_minutes_per_day", None),
        }


@dataclass
class Pet:
    id: str
    owner_id: str
    name: str
    species: str
    age: int
    health_notes: Optional[str] = None
    default_tasks: List[str] = field(default_factory=list)

    def update_profile(self, **kwargs: Any) -> None:
        """Update pet attributes from provided keyword values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def needs_today(self, _target_date: date) -> List[str]:
        """Return the pet's default tasks for the requested day."""
        return self.default_tasks.copy()

    def is_high_priority(self) -> bool:
        """Check whether the pet has urgent care needs."""
        return "urgent" in (self.health_notes or "").lower()


@dataclass
class Task:
    id: str
    title: str
    pet_id: str
    duration: int
    priority: int
    due_time: Optional[datetime] = None
    recurrence: Optional[str] = None
    scheduled_date: Optional[date] = None
    status: str = "pending"
    notes: Optional[str] = None

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def reschedule(self, new_time: datetime) -> None:
        """Move the task to a new due time and scheduled date."""
        self.due_time = new_time
        self.scheduled_date = new_time.date()

    def update_details(self, **kwargs: Any) -> None:
        """Update task attributes from provided keyword values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def is_overdue(self, reference: Optional[datetime] = None) -> bool:
        """Return whether the task is overdue at the reference time."""
        reference = reference or datetime.now()
        if self.due_time is None:
            return False
        return self.due_time < reference and self.status != "completed"

    def effective_score(self, now: Optional[datetime] = None) -> float:
        """Compute a score using task priority plus time urgency."""
        now = now or datetime.now()
        base = self.priority * 10
        if self.due_time is not None:
            seconds_left = (self.due_time - now).total_seconds()
            urgency = max(0.0, 7200 - seconds_left) / 3600
            return base + urgency
        return float(base)


@dataclass
class Slot:
    id: str
    task: Task
    start_time: datetime
    end_time: datetime

    def duration(self) -> int:
        """Return the slot length in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)


@dataclass
class TaskManager:
    tasks: List[Task] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)
    owners: List[Owner] = field(default_factory=list)

    def add_owner(self, owner: Owner) -> None:
        """Add an owner if an equivalent record does not already exist."""
        if any(existing.name == owner.name for existing in self.owners):
            raise ValueError(f"Owner named '{owner.name}' already exists")
        self.owners.append(owner)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet if its identifier is unique."""
        if any(existing.id == pet.id for existing in self.pets):
            raise ValueError(f"Pet with id '{pet.id}' already exists")
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a task if its identifier is unique."""
        if any(existing.id == task.id for existing in self.tasks):
            raise ValueError(f"Task with id '{task.id}' already exists")
        self.tasks.append(task)

    def edit_task(self, task_id: str, **updates: Any) -> None:
        """Apply updates to an existing task by id."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            raise ValueError(f"Task with id '{task_id}' not found")
        task.update_details(**updates)

    def delete_task(self, task_id: str) -> None:
        """Remove a task with the matching id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks_by_day(self, target_date: date) -> List[Task]:
        """Return tasks scheduled or due on the target date."""
        return [
            task
            for task in self.tasks
            if task.scheduled_date == target_date
            or (
                task.due_time is not None
                and task.due_time.date() == target_date
            )
        ]

    def get_tasks_by_pet(self, pet_id: str) -> List[Task]:
        """Return all tasks assigned to the given pet."""
        return [t for t in self.tasks if t.pet_id == pet_id]

    def get_pending_tasks(self) -> List[Task]:
        """Return all tasks that are not completed."""
        return [t for t in self.tasks if t.status != "completed"]

    def load(self, data: Any) -> None:
        """Populate owners, pets, and tasks from serialized data."""
        self.tasks = [Task(**item) for item in data.get("tasks", [])]
        self.pets = [Pet(**item) for item in data.get("pets", [])]
        self.owners = [Owner(**item) for item in data.get("owners", [])]

    def save(self) -> Any:
        """Serialize owners, pets, and tasks to a dictionary."""
        return {
            "tasks": [task.__dict__ for task in self.tasks],
            "pets": [pet.__dict__ for pet in self.pets],
            "owners": [owner.__dict__ for owner in self.owners],
        }


@dataclass
class DailySchedule:
    date: date
    slots: List[Slot] = field(default_factory=list)
    total_duration: int = 0
    unscheduled_tasks: List[Task] = field(default_factory=list)
    reasoning: Optional[str] = None

    def add_slot(self, slot: Slot) -> None:
        """Add a slot and update the schedule duration."""
        self.slots.append(slot)
        self.total_duration += slot.duration()

    def remove_slot(self, slot_id: str) -> None:
        """Remove a slot by id and recalculate total duration."""
        self.slots = [slot for slot in self.slots if slot.id != slot_id]
        self.total_duration = sum(slot.duration() for slot in self.slots)

    def get_today_tasks(self) -> List[Slot]:
        """Return the scheduled slots for this day."""
        return self.slots

    def get_unplanned_tasks(self) -> List[Task]:
        """Return tasks that could not be scheduled."""
        return self.unscheduled_tasks

    def describe(self) -> str:
        """Build a readable summary of the daily schedule."""
        lines = [
            f"Daily schedule for {self.date.isoformat()}: "
            f"{len(self.slots)} slots"
        ]
        for slot in self.slots:
            lines.append(
                f"- {slot.task.title} ({slot.duration()} min) at "
                f"{slot.start_time.time()} to {slot.end_time.time()}"
            )
        if self.reasoning:
            lines.append(f"Reasoning: {self.reasoning}")
        return "\n".join(lines)


@dataclass
class Scheduler:
    agenda: DailySchedule = field(
        default_factory=lambda: DailySchedule(date.today())
    )
    constraints: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)

    def generate_daily_plan(
        self, task_manager: TaskManager, target_date: date
    ) -> DailySchedule:
        """Generate and store a plan for the target date."""
        available_tasks = task_manager.get_tasks_by_day(target_date)
        if not available_tasks:
            available_tasks = task_manager.get_pending_tasks()

        ranked_tasks = self.rank_tasks(available_tasks)
        plan = self.fit_tasks_into_slots(ranked_tasks, target_date)
        plan.reasoning = self.explain_plan()
        self.agenda = plan
        return plan

    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks from highest to lowest effective score."""
        return sorted(tasks, key=lambda t: t.effective_score(), reverse=True)

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by due time, placing undated tasks last."""
        return sorted(
            tasks,
            key=lambda task: (task.due_time is None, task.due_time),
        )

    def filter_tasks(
        self,
        task_manager: TaskManager,
        status: Optional[str] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by completion status, pet name, or both."""
        pet_ids = None
        if pet_name is not None:
            pet_name_lower = pet_name.lower()
            pet_ids = {
                pet.id
                for pet in task_manager.pets
                if pet.name.lower() == pet_name_lower
            }

        filtered_tasks = []
        for task in task_manager.tasks:
            if status is not None and task.status != status:
                continue
            if pet_ids is not None and task.pet_id not in pet_ids:
                continue
            filtered_tasks.append(task)

        return filtered_tasks

    def fit_tasks_into_slots(
        self, tasks: List[Task], target_date: date
    ) -> DailySchedule:
        """Pack ranked tasks into sequential slots for the day."""
        plan = DailySchedule(date=target_date)
        start_of_day = datetime.combine(
            target_date, datetime.min.time()
        ).replace(hour=8, minute=0)
        max_minutes = self.constraints.get("max_minutes", 480)
        used_minutes = 0

        for task in tasks:
            if used_minutes + task.duration > max_minutes:
                plan.unscheduled_tasks.append(task)
                continue

            slot_start = start_of_day + timedelta(minutes=used_minutes)
            slot_end = slot_start + timedelta(minutes=task.duration)
            slot = Slot(
                id=f"slot_{task.id}",
                task=task,
                start_time=slot_start,
                end_time=slot_end,
            )
            plan.add_slot(slot)
            used_minutes += task.duration
            task.scheduled_date = target_date

        return plan

    def explain_plan(self) -> str:
        """Explain the scheduler's task ordering and packing strategy."""
        return (
            "Tasks are prioritized by effective score and packed sequentially "
            "into available free time."
        )

    def adjust_plan(
        self, plan: DailySchedule, updates: Dict[str, Any]
    ) -> DailySchedule:
        """Apply supported edits to an existing schedule."""
        if "remove_task_id" in updates:
            plan.remove_slot(updates["remove_task_id"])
        return plan
