from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional, Any

@dataclass
class Owner:
    name: str
    contact_info: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    available_hours: List[Dict[str, Any]] = field(default_factory=list)

    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        pass

    def set_availability(self, availability: List[Dict[str, Any]]) -> None:
        pass

    def get_daily_constraints(self, target_date: date) -> Dict[str, Any]:
        pass

@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: Optional[str] = None
    default_tasks: List[str] = field(default_factory=list)

    def update_profile(self, **kwargs: Any) -> None:
        pass

    def needs_today(self, target_date: date) -> List[str]:
        pass

    def is_high_priority(self) -> bool:
        pass

@dataclass
class Task:
    id: str
    title: str
    pet_id: str
    duration: int
    priority: int
    due_time: Optional[datetime] = None
    recurrence: Optional[str] = None
    status: str = "pending"
    notes: Optional[str] = None

    def mark_completed(self) -> None:
        pass

    def reschedule(self, new_time: datetime) -> None:
        pass

    def update_details(self, **kwargs: Any) -> None:
        pass

    def is_overdue(self, reference: Optional[datetime] = None) -> bool:
        pass

    def effective_score(self, now: Optional[datetime] = None) -> float:
        pass

@dataclass
class TaskManager:
    tasks: List[Task] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)
    owners: List[Owner] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, task_id: str, **updates: Any) -> None:
        pass

    def delete_task(self, task_id: str) -> None:
        pass

    def get_tasks_by_day(self, target_date: date) -> List[Task]:
        pass

    def get_tasks_by_pet(self, pet_id: str) -> List[Task]:
        pass

    def get_pending_tasks(self) -> List[Task]:
        pass

    def load(self, data: Any) -> None:
        pass

    def save(self) -> Any:
        pass

@dataclass
class DailySchedule:
    date: date
    slots: List[Dict[str, Any]] = field(default_factory=list)
    total_duration: int = 0
    unscheduled_tasks: List[Task] = field(default_factory=list)
    reasoning: Optional[str] = None

    def add_slot(self, task: Task, start_time: datetime) -> None:
        pass

    def remove_slot(self, slot_id: str) -> None:
        pass

    def get_today_tasks(self) -> List[Dict[str, Any]]:
        pass

    def get_unplanned_tasks(self) -> List[Task]:
        pass

    def describe(self) -> str:
        pass

@dataclass
class Scheduler:
    agenda: DailySchedule = field(default_factory=lambda: DailySchedule(date.today()))
    constraints: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)

    def generate_daily_plan(self, task_manager: TaskManager, target_date: date) -> DailySchedule:
        pass

    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        pass

    def fit_tasks_into_slots(self, tasks: List[Task], target_date: date) -> DailySchedule:
        pass

    def explain_plan(self) -> str:
        pass

    def adjust_plan(self, plan: DailySchedule, updates: Dict[str, Any]) -> DailySchedule:
        pass
