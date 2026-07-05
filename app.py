import io
import contextlib
from datetime import date

import streamlit as st
from pawpal_system import Owner, Pet, Task, Planner, format_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
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

# Show any scheduling conflicts above the task list. conflict_warnings() never
# raises, so a bad time can't crash the app.
for message in planner.conflict_warnings(owner.pets):
    st.warning(message)

# List each task with a Complete button. Completing a daily/weekly task marks it
# done and auto-creates its next occurrence. Only show tasks due today or earlier,
# so an upcoming repeat stays hidden until its day and the list isn't cluttered
# with tasks that aren't for today.
today = date.today()
for pet, task in planner.sort_tasks_by_time(owner.pets):
    if task.due_date > today:
        continue
    row, action = st.columns([6, 1])
    with row:
        mark = "✅" if task.completed else "⬜️"
        repeats = "" if task.recurrence == "none" else f" · repeats {task.recurrence}"
        st.write(
            f"{mark} **{task.description}** — {pet.name} · due {task.due_date} "
            f"at {format_time(task.time)} · {task.duration_minutes} min · {task.priority}{repeats}"
        )
    with action:
        # id(task) gives each button a stable, unique key even for same-named tasks.
        if not task.completed and st.button("Complete", key=f"complete_{id(task)}"):
            planner.mark_task_complete(pet, task)
            st.rerun()

if st.button("Generate schedule"):
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
        for pet, task in matches:
            mark = "✅" if task.completed else "⬜️"
            st.write(
                f"{mark} **{task.description}** — {pet.name} · due {task.due_date} "
                f"at {format_time(task.time)} · {task.priority}"
            )
    else:
        st.info("No tasks match those filters.")
else:
    st.info("Add a pet and some tasks first, then you can filter them.")
