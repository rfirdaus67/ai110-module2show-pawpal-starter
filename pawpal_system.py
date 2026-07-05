from dataclasses import dataclass


class Pet:
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self.tasks = []

    @property
    def task_count(self):
        return len(self.tasks)

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Task:
    description: str
    time: str
    duration_minutes: int
    priority: int
    completed: bool = False

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True


class Owner:
    def __init__(self, name: str, available_start: str, available_end: str):
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
        print("\n--- Today's Schedule ---")

        # Gather every task across all pets and order by priority (1 = highest, at top)
        all_tasks = [(pet, task) for pet in pets for task in pet.tasks]
        all_tasks.sort(key=lambda pair: pair[1].priority)

        for pet, task in all_tasks:
            status = "Completed" if task.completed else "Not completed"
            print(
                f" [Priority #{task.priority}] {pet.name}: {task.description} "
                f"for {pet.name} at {task.time} ({task.duration_minutes} min) - {status}"
            )

        # --- Summary ---
        total_all_duration = sum(task.duration_minutes for _, task in all_tasks)
        print("\n--- Summary ---")

        for pet in pets:
            print(f"{pet.name}: {pet.task_count} tasks")
        print(f"TOTAL DURATION (ALL PETS): {total_all_duration} minutes")