from asyncio import all_tasks
from dataclasses import dataclass


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
    time: str
    duration_minutes: int
    priority: str
    completed: bool = False

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True


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

    def print_summary(self, pets):
        """Prints all tasks sorted by priority, then a per-pet and total summary."""
        print("\n--- Today's Schedule ---")

        # Gather every task across all pets and order by priority (1 = highest, at top)
        all_tasks = [(pet, task) for pet in pets for task in pet.tasks]
        priority_order = {
            "high": 1,
             "medium": 2,
            "low": 3
        }
        all_tasks.sort(key=lambda pair: priority_order[pair[1].priority])

        for pet, task in all_tasks:
            status = "Completed" if task.completed else "Not completed"
            print(
                f"[{task.priority.capitalize()} Priority] "
                f"{pet.name}: {task.description} "
                f"at {task.time} ({task.duration_minutes} min) - {status}"
            )

        print("\n--- Plan Explanation ---")
        for pet, task in all_tasks:
            print(
                f"- {pet.name}'s '{task.description}' is scheduled at {task.time} "
                f"because it is a {task.priority} priority task. "
                f"It takes {task.duration_minutes} minutes."
            )

        # --- Summary ---
        total_all_duration = sum(task.duration_minutes for _, task in all_tasks)
        print("\n--- Summary ---")

        for pet in pets:
            print(f"{pet.name}: {pet.task_count} tasks")
        print(f"TOTAL DURATION (ALL PETS): {total_all_duration} minutes")