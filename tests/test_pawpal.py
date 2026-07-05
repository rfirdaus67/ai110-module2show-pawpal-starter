from pawpal_system import Task, Pet


def test_task_completion():
    task = Task("Morning Walk", "8:00 am", 30, 1)

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition_to_pet():
    pet = Pet("Mittens", "Cat")

    initial_count = len(pet.tasks)

    task = Task("Feed Cat", "9:00 am", 10, 2)
    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
