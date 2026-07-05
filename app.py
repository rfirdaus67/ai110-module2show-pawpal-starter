import io
import contextlib

import streamlit as st
from pawpal_system import Owner, Pet, Task, Planner

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
        task_time = st.text_input("Time", value="8:00 am")
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == assigned_to)
        planner.add_task(
            pet,
            Task(task_title, task_time, int(duration), priority),
        )
        st.success(f"Added '{task_title}' for {pet.name}.")
else:
    st.info("Add a pet first, then you can schedule tasks for it.")

st.divider()

st.subheader("Build Schedule")
st.caption("Sorts all tasks by priority and prints a per-pet summary.")

if st.button("Generate schedule"):
    # print_summary() writes to stdout, so capture it and show it in the app.
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        planner.print_summary(owner.pets)
    st.code(buffer.getvalue() or "No tasks scheduled yet.")
