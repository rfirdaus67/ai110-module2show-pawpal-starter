from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: int
    completed: bool = False
    pet: Pet

    def mark_complete(self):
        """Marks the task as completed."""
        pass


class Owner:
    def __init__(self, name: str, available_start: str, available_end: str):
        self.name = name
        self.available_start = available_start
        self.available_end = available_end
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Adds a pet to the owner's list of pets."""
        pass


class Planner:
    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Adds a task to the planner."""
        pass

    def generate_plan(self, owner: Owner):
        """Generates a plan based on the owner's availability."""
        pass

    def explain_plan(self):
        """Explains the generated plan."""
        pass

    def get_total_duration(self):
        """Returns the total duration of all tasks."""
        pass