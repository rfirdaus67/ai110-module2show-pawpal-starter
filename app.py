import io
import contextlib
from datetime import date

import streamlit as st
from pawpal_system import Owner, Pet, Task, Planner, format_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    "A pet care planning assistant. Add your pets and their care tasks, then build a "
    "daily schedule that's sorted by time, flags conflicts, and handles recurring tasks."
)

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
owner_start = st.text_input("Available from", value="8:00 am")
owner_end = st.text_input("Available until", value="6:00 pm")

# Create the Owner and Planner once, then persist them across reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, owner_start, owner_end)
if "planner" not in st.session_state:
    st.session_state.planner = Planner()

owner = st.session_state.owner
planner = st.session_state.planner

st.divider()

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))
    st.success(f"Added {pet_name} the {species}.")

if owner.pets:
    st.write("Current pets:", ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")

if owner.pets:
    assigned_to = st.selectbox("Assign task to", [p.name for p in owner.pets])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        # Time is stored as minutes since midnight, so collect hour + minute as numbers.
        hour = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=8)
        minute = st.number_input("Minute", min_value=0, max_value=59, value=0)
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"])

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == assigned_to)
        task_time = int(hour) * 60 + int(minute)
        planner.add_task(
            pet,
            Task(task_title, task_time, int(duration), priority, recurrence=recurrence),
        )
        st.success(f"Added '{task_title}' for {pet.name}.")
else:
    st.info("Add a pet first, then you can schedule tasks for it.")

st.divider()

st.subheader("Build Today's Schedule 🗓️")
st.caption("Sorts all tasks by time, flags scheduling conflicts, and prints a per-pet summary.")


# --- Conflict detection ---
# conflict_warnings() never raises, so a bad time can't crash the app.
# Show a warning per overlap, or a green all-clear when there are none.
warnings = planner.conflict_warnings(owner.pets)
if warnings:
    for message in warnings:
        st.warning(f"⚠️ {message}")
else:
    st.success("✅ No scheduling conflicts — every task has its own time slot.")

# --- Sorted schedule (chronological, today or earlier) ---
# sort_tasks_by_time() returns (pet, task) pairs ordered by start time. Upcoming
# repeats are hidden until their day so the list isn't cluttered with future copies.
today = date.today()
schedule = [
    (pet, task)
    for pet, task in planner.sort_tasks_by_time(owner.pets)
    if task.due_date <= today
]

if schedule:
    st.table(
        [
            {
                "Status": "✅ Done" if task.completed else "⬜️ To do",
                "Time": format_time(task.time),
                "Task": task.description,
                "Pet": pet.name,
                "Due": str(task.due_date),
                "Duration": f"{task.duration_minutes} min",
                "Priority": task.priority.capitalize(),
                "Repeats": "—" if task.recurrence == "none" else task.recurrence.capitalize(),
            }
            for pet, task in schedule
        ]
    )

    # --- Recurrence ---
    # Completing a daily/weekly task auto-creates its next occurrence. Pick an
    # open task and complete it; the confirmation shows the next due date.
    open_tasks = [(pet, task) for pet, task in schedule if not task.completed]
    if open_tasks:
        chosen = st.selectbox(
            "Mark a task complete",
            range(len(open_tasks)),
            format_func=lambda i: (
                f"{open_tasks[i][1].description} — {open_tasks[i][0].name} "
                f"at {format_time(open_tasks[i][1].time)}"
            ),
        )
        if st.button("Complete task ✅"):
            pet, task = open_tasks[chosen]
            new_task = planner.mark_task_complete(pet, task)
            if new_task is not None:
                st.success(
                    f"Completed '{task.description}'. Next {task.recurrence} occurrence "
                    f"scheduled for {new_task.due_date}."
                )
            else:
                st.success(f"Completed '{task.description}'.")
            st.rerun()
    else:
        st.info("All of today's tasks are done. 🎉")
else:
    st.info("No tasks scheduled for today yet. Add some above.")

if st.button("Generate schedule summary"):
    # print_summary() writes to stdout, so capture it and show it as text.
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        planner.print_summary(owner.pets)
    st.text(buffer.getvalue() or "No tasks scheduled yet.")

st.divider()

st.subheader("Filter Tasks 🔍")
st.caption("Narrow the task list by pet, status, and/or priority. 'All' ignores that filter.")

if owner.pets:
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        pet_choice = st.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets])
    with fcol2:
        status_choice = st.selectbox("Status", ["All", "To do", "Completed"])
    with fcol3:
        priority_choice = st.selectbox("Priority", ["All", "high", "medium", "low"])

    # Translate the "All" picks into None so filter_tasks ignores those criteria.
    pet_name = None if pet_choice == "All pets" else pet_choice
    completed = {"All": None, "To do": False, "Completed": True}[status_choice]
    priority = None if priority_choice == "All" else priority_choice

    matches = planner.filter_tasks(
        owner.pets, pet_name=pet_name, completed=completed, priority=priority
    )
    if matches:
        st.table(
            [
                {
                    "Status": "✅ Done" if task.completed else "⬜️ To do",
                    "Time": format_time(task.time),
                    "Task": task.description,
                    "Pet": pet.name,
                    "Due": str(task.due_date),
                    "Priority": task.priority.capitalize(),
                }
                for pet, task in matches
            ]
        )
    else:
        st.info("No tasks match those filters.")
else:
    st.info("Add a pet and some tasks first, then you can filter them.")
