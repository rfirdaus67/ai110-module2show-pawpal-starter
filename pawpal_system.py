from dataclasses import dataclass, field
from datetime import date, timedelta

# How many days forward each recurrence repeats.
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


def format_time(minutes):
    """Turns minutes since midnight (e.g. 480) into a friendly '8:00 am' string."""
    hours, mins = divmod(minutes % (24 * 60), 60)
    meridiem = "am" if hours < 12 else "pm"
    display_hour = hours % 12 or 12
    return f"{display_hour}:{mins:02d} {meridiem}"


class Pet:
    def __init__(self, name, species):
        """Creates a pet with a name, species, and an empty task list."""
        self.name = name
        self.species = species
        self.tasks = []

    @property
    def task_count(self):
        """Returns the number of tasks assigned to this pet."""
        return len(self.tasks)

    def add_task(self, task):
        """Adds a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task):
        """Removes a task from this pet's task list if present."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Task:
    description: str
    time: int  # minutes since midnight, e.g. 8:00 am -> 480, 5:00 pm -> 1020
    duration_minutes: int
    priority: str
    completed: bool = False
    recurrence: str = "none"  # "none", "daily", or "weekly"
    due_date: date = field(default_factory=date.today)  # defaults to today

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True

    def next_due_date(self):
        """Next occurrence's due date (today + 1 day for daily, + 7 for weekly), or None if it doesn't repeat."""
        if self.recurrence in RECURRENCE_DAYS:
            return date.today() + timedelta(days=RECURRENCE_DAYS[self.recurrence])
        return None

    @property
    def end_minutes(self):
        """When the task finishes, so we can tell if two tasks overlap."""
        return self.time + self.duration_minutes

    def overlaps(self, other):
        """True if this task's time window collides with another task's window."""
        return self.time < other.end_minutes and other.time < self.end_minutes


class Owner:
    def __init__(self, name: str, available_start: str, available_end: str):
        """Creates an owner with a name, availability window, and no pets."""
        self.name = name
        self.available_start = available_start
        self.available_end = available_end
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Adds a pet to the owner's list of pets."""
        self.pets.append(pet)


class Planner:
    def add_task(self, pet: Pet, task: Task):
        """Assigns a task to a pet so the pet stores its own tasks."""
        pet.add_task(task)

    def mark_task_complete(self, pet: Pet, task: Task):
        """Marks a task complete; for a recurring task, adds a fresh copy on its next due date. Returns the new Task or None."""
        task.mark_complete()

        next_date = task.next_due_date()
        if next_date is None:
            return None

        next_task = Task(
            description=task.description,
            time=task.time,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            recurrence=task.recurrence,
            due_date=next_date,
        )
        pet.add_task(next_task)
        return next_task

    def _collect_tasks(self, pets):
        """Helper: gathers every pet's tasks into a flat list of (pet, task) pairs.

        Keeping the pet paired with each task lets the sorting, filtering, and
        conflict methods know which pet a task belongs to.
        """
        return [(pet, task) for pet in pets for task in pet.tasks]

    def sort_tasks_by_time(self, pets):
        """Returns all (pet, task) pairs ordered by start time, earliest first.

        Because a task's time is stored as minutes since midnight, sorting is a
        simple numeric comparison of that value.
        """
        return sorted(self._collect_tasks(pets), key=lambda pair: pair[1].time)

    def filter_tasks(self, pets, pet_name=None, completed=None, priority=None):
        """Returns (pet, task) pairs matching the given criteria; a criterion left as None is ignored."""
        results = []
        for pet, task in self._collect_tasks(pets):
            if pet_name is not None and pet.name != pet_name:
                continue
            if completed is not None and task.completed != completed:
                continue
            if priority is not None and task.priority != priority:
                continue
            results.append((pet, task))
        return results

    def detect_conflicts(self, pets):
        """Returns pairs of same-day, incomplete tasks whose time windows overlap."""
        # Sorting by (due_date, time) keeps same-day tasks adjacent, so we only compare neighbors.
        scheduled = sorted(
            (pair for pair in self._collect_tasks(pets) if not pair[1].completed),
            key=lambda pair: (pair[1].due_date, pair[1].time),
        )
        conflicts = []
        for current, following in zip(scheduled, scheduled[1:]):
            same_day = current[1].due_date == following[1].due_date
            if same_day and current[1].overlaps(following[1]):
                conflicts.append((current, following))
        return conflicts

    def conflict_warnings(self, pets):
        """Crash-proof conflict check: returns a list of warning strings (empty if none), never raises."""
        try:
            return [
                f"{pet_a.name}'s '{task_a.description}' ({format_time(task_a.time)}) overlaps "
                f"{pet_b.name}'s '{task_b.description}' ({format_time(task_b.time)}) on {task_a.due_date}"
                for (pet_a, task_a), (pet_b, task_b) in self.detect_conflicts(pets)
            ]
        except Exception:
            return ["Couldn't check for conflicts — please double-check the task times."]

    def print_summary(self, pets):
        """Prints tasks sorted by time, flags conflicts, then a per-pet and total summary."""
        print("\n--- Today's Schedule (by time) ---")

        scheduled = self.sort_tasks_by_time(pets)
        for pet, task in scheduled:
            status = "Completed" if task.completed else "Not completed"
            repeats = "" if task.recurrence == "none" else f" [repeats {task.recurrence}]"
            print(
                f"[{task.priority.capitalize()} Priority] "
                f"{pet.name}: {task.description} "
                f"on {task.due_date} at {format_time(task.time)} "
                f"({task.duration_minutes} min) - {status}{repeats}"
            )

        conflicts = self.detect_conflicts(pets)
        print("\n--- Conflicts ---")
        if conflicts:
            for (pet_a, task_a), (pet_b, task_b) in conflicts:
                print(
                    f"! {pet_a.name}'s '{task_a.description}' ({format_time(task_a.time)}) overlaps "
                    f"{pet_b.name}'s '{task_b.description}' ({format_time(task_b.time)})"
                )
        else:
            print("None — no overlapping tasks.")

        print("\n--- Plan Explanation ---")
        # A recurring task can have several occurrences (e.g. today + future copies).
        # Explain each distinct task only once so the plan isn't repetitive.
        explained = set()
        for pet, task in scheduled:
            key = (pet.name, task.description, task.time)
            if key in explained:
                continue
            explained.add(key)
            print(
                f"- {pet.name}'s '{task.description}' is scheduled at {format_time(task.time)} "
                f"because it is a {task.priority} priority task. "
                f"It takes {task.duration_minutes} minutes."
            )

        # --- Summary ---
        total_all_duration = sum(task.duration_minutes for _, task in scheduled)
        print("\n--- Summary ---")
        for pet in pets:
            print(f"{pet.name}: {pet.task_count} tasks")
        print(f"TOTAL DURATION (ALL PETS): {total_all_duration} minutes")
