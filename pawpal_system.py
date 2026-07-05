from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str



@dataclass
class Task:
    description: str
    time: str
    duration_minutes: int
    priority: int
    pet: Pet
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
    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Adds a task to the planner."""
        self.tasks.append(task)


    def generate_plan(self, owner: Owner):
        """Generates a plan based on the owner's availability."""
        self.tasks.sort(key=lambda task: task.priority)

    def explain_plan(self):
        """Explains the generated plan."""
        print("Today's Schedule")
        print("----------------")

        for task in self.tasks:
            status = "Completed" if task.completed else "Not Completed"
            print(
                f"{task.pet.name} ({task.time}) - "
                f"{task.description} ({task.duration_minutes} mins) - {status}"
            )

    def get_total_duration(self):
        """Returns the total duration of all tasks."""
        return sum(task.duration_minutes for task in self.tasks)