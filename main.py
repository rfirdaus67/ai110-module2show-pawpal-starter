from pawpal_system import Owner, Pet, Task, Planner

owner = Owner("Alice", "8:00", "6:00")

dog = Pet("Buddy", "Dog")
cat = Pet("Mittens", "Cat")

owner.add_pet(dog)
owner.add_pet(cat)

planner = Planner()

# time is stored as minutes since midnight: 8 * 60 = 8:00 am, 17 * 60 = 5:00 pm.
planner.add_task(dog, Task("Take Buddy for a walk", 8 * 60, 30, "high", recurrence="daily"))
planner.add_task(cat, Task("Feed Mittens her breakfast", 9 * 60, 10, "medium"))
# This one starts at 8:10 am while the walk (8:00-8:30) is still going -> a conflict.
planner.add_task(cat, Task("Give Mittens her medicine", 8 * 60 + 10, 5, "high"))
planner.add_task(dog, Task("Evening walk", 17 * 60, 30, "low", recurrence="daily"))

planner.print_summary(owner.pets)

# --- Demonstrate the filtering helper ---
print("\n--- High-priority tasks only ---")
for pet, task in planner.filter_tasks(owner.pets, priority="high"):
    print(f"{pet.name}: {task.description}")
