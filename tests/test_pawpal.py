from datetime import date, timedelta

from pawpal_system import Task, Pet, Planner


TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)


def test_task_completion():
    task = Task("Morning Walk", 480, 30, "high")

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition_to_pet():
    pet = Pet("Mittens", "Cat")

    initial_count = len(pet.tasks)

    task = Task("Feed Cat", 540, 10, "medium")
    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1


# ===========================================================================
# 1. SORTING CORRECTNESS — tasks returned in chronological (start-time) order
# ===========================================================================

# --- happy path ---
def test_sort_returns_tasks_in_chronological_order():
    pet = Pet("Rex", "Dog")
    # Added out of order on purpose.
    pet.add_task(Task("Dinner", 1020, 20, "high"))     # 5:00 pm
    pet.add_task(Task("Breakfast", 480, 15, "high"))   # 8:00 am
    pet.add_task(Task("Lunch", 720, 15, "medium"))     # 12:00 pm

    ordered = Planner().sort_tasks_by_time([pet])

    assert [task.description for _, task in ordered] == ["Breakfast", "Lunch", "Dinner"]


# --- edge case: a pet with no tasks ---
def test_sort_pet_with_no_tasks_returns_empty_list():
    pet = Pet("Ghost", "Cat")

    assert Planner().sort_tasks_by_time([pet]) == []


# --- edge case: two tasks at the exact same time (stable, both kept) ---
def test_sort_keeps_both_tasks_at_identical_times():
    pet = Pet("Rex", "Dog")
    pet.add_task(Task("Pill", 480, 5, "high"))     # 8:00 am
    pet.add_task(Task("Feed", 480, 10, "high"))    # 8:00 am

    ordered = Planner().sort_tasks_by_time([pet])
    times = [task.time for _, task in ordered]

    assert len(ordered) == 2
    assert times == [480, 480]


# ===========================================================================
# 2. RECURRENCE LOGIC — completing a daily task creates one for the next day
# ===========================================================================

# --- happy path: daily task due today -> new copy due tomorrow ---
def test_completing_daily_task_creates_task_for_next_day():
    planner = Planner()
    pet = Pet("Bella", "Cat")
    task = Task("Feed", 480, 10, "high", recurrence="daily", due_date=TODAY)
    pet.add_task(task)

    new_task = planner.mark_task_complete(pet, task)

    assert task.completed is True
    assert new_task is not None
    assert new_task.completed is False
    assert new_task.due_date == TOMORROW
    assert new_task.description == task.description
    assert len(pet.tasks) == 2


# --- happy path: weekly task -> new copy seven days later ---
def test_completing_weekly_task_creates_task_seven_days_later():
    planner = Planner()
    pet = Pet("Duke", "Dog")
    task = Task("Bath", 600, 45, "medium", recurrence="weekly", due_date=TODAY)
    pet.add_task(task)

    new_task = planner.mark_task_complete(pet, task)

    assert new_task is not None
    assert new_task.due_date == TODAY + timedelta(days=7)


# --- edge case: non-recurring task creates no follow-up ---
def test_completing_non_recurring_task_creates_no_new_task():
    planner = Planner()
    pet = Pet("Spot", "Dog")
    task = Task("Vet Visit", 600, 30, "high", recurrence="none")
    pet.add_task(task)

    new_task = planner.mark_task_complete(pet, task)

    assert task.completed is True
    assert new_task is None
    assert len(pet.tasks) == 1


# ===========================================================================
# 3. CONFLICT DETECTION — overlapping same-day tasks are flagged
# ===========================================================================

# --- happy path: two overlapping tasks flagged ---
def test_detect_conflicts_flags_overlapping_tasks():
    pet = Pet("Duke", "Dog")
    pet.add_task(Task("Walk", 480, 60, "high"))    # 8:00-9:00
    pet.add_task(Task("Groom", 510, 30, "low"))    # 8:30-9:00

    conflicts = Planner().detect_conflicts([pet])

    assert len(conflicts) == 1


# --- edge case: two tasks at the exact same time (duplicate) ---
def test_detect_conflicts_flags_duplicate_times():
    pet = Pet("Milo", "Cat")
    pet.add_task(Task("A", 480, 30, "high"))       # 8:00-8:30
    pet.add_task(Task("B", 480, 30, "low"))        # 8:00-8:30 (same time)

    conflicts = Planner().detect_conflicts([pet])

    assert len(conflicts) == 1


# --- edge case: back-to-back tasks do NOT conflict ---
def test_detect_conflicts_ignores_back_to_back_tasks():
    pet = Pet("Ziggy", "Dog")
    pet.add_task(Task("A", 480, 60, "high"))       # 8:00-9:00
    pet.add_task(Task("B", 540, 30, "low"))        # 9:00-9:30 (touching, not overlapping)

    conflicts = Planner().detect_conflicts([pet])

    assert conflicts == []


# --- edge case: same time on different days does NOT conflict ---
def test_detect_conflicts_ignores_same_time_on_different_days():
    pet = Pet("Ash", "Cat")
    pet.add_task(Task("A", 480, 30, "high", due_date=TODAY))
    pet.add_task(Task("B", 480, 30, "low", due_date=TOMORROW))

    conflicts = Planner().detect_conflicts([pet])

    assert conflicts == []


# --- edge case: a pet with no tasks has no conflicts ---
def test_detect_conflicts_pet_with_no_tasks():
    pet = Pet("Ghost", "Cat")

    assert Planner().detect_conflicts([pet]) == []
