# PawPal+ Project Reflection

## 1. System Design

1. Add a pet and owner
2. Allow the owner to label their available times that day
3. Schedule a walk
4. Make a task list

Classes:
1. Owner
    - Attributes: name, available_start, available_end, pets
    - Methods: add_pet(pet)
2. Pet
   - Attributes: name, species
3. Task
    - Attributes: title, duration_minutes, priority, completed
    - Methods: mark_complete()
4. Planner
    - Attributes: tasks
    - Methods: add_task(task), generate_plan(owner), explain_plan(), get_total_duration()
    
**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design had four classes, an Owner class, Pet class, Task class, and Planner class. The Owner class stores the owner's name, available times, and list of pets. The Pet class stores basic information stores the pet name and species. The Task class represents tasks like walks or feeding and keeps track of their duration, priority, and completion. The Planner class is responsible for managing tasks and creates a schedule based on the owner's availability, explains the plan, and calculates the total time needed for the specified tasks.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, I made one change which was adding a Pet object under each Task. That way, it is less vague which task is referring to which pet if an owner has multiple pets and a task is linked to a specific pet. I also added time, so the user can plan ahead of time when they are supposed to be completing that task, in addition to the duration. Also changed the "title" attribute for the Task class to "description" because the description would be saying the same thing and allowing for more notes/details by the user.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers time and priority the most. I decided that time mattered the most because I could either choose to have tasks be organized top to bottom based on time or priority. However, I felt time was more important here because it's easier for the user to read through and they have a timeline they can check off as their day goes on. I felt this allowed for better readability than priority. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my schedular makes is that the schedule only advances (especially for daily and weekly tasks) when you check task's off. Also to make the schedule not look so clunky, while it would make sense to keep displaying incoming tasks for repeating daily/weekly tasks, I chose to keep it strictly to "Today's Schedule". So if a task doesn't get checked off, then tomorrow's task never gets created and won't display. This goes against the whole point of the daily/weekly task system.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI like Claude and ChatGPT for designing and fixing UI in steamlit, making pytests to properly test to program and also debugging when my expected output wasn't reflected in main.py or my streamlit app.

The most helpful prompts were the ones that were most specific and also using what CodePath already gave. Also breaking tasks up with concise language and being in the right files/code lines, so it was easier for the AI to go through. Persona prompting also helped like asking the AI to act like a python developer so they thought from my perspective.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment I didn't accept an AI suggestion was when it came to how to store a task's time. The AI first suggested keeping the time as a string like "8:00 am" and writing a helper function to parse it into minutes before sorting. However, this seemed very lengthy when I looked at the code and I originally had put time as a string, so I wouldn't have to worry about formatting. It seemed like an extra place for bugs (for example, "10:00 am" sorting before "8:00 am" as plain text). Instead, I decided to store the time as an integer (minutes since midnight), which made sorting simpler. I verified this by running main.py and checking the schedule printed in the correct chronological order, and by testing in the Streamlit app that a task at 8:10 correctly flagged a conflict with an 8:00–8:30 walk.

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote multiple pytests with the first couple of tests going to the app's functionality and basic object behavior and if marking a task as complete truly worked. I also confirmed tasks were properly added to a pet. I then tested the scheduler's sorting logic by making sure tasks were in chronological order even when they are added out of order (based on time). I tested "happy" and edge cases, including pets with no tasks and multiple tasks scheduled for the exact same time to ensure they were both preserved. 

These tests were important because they ensured that both the app has basic functionality and wouldn't crash while also making sure less common edge cases behaved correctly. These were still real issues the user could run into and I wanted to make sure my app would still work.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident that my scheduler works correctly because I tested "happy" cases and edge cases using pytest. I also made sure to manually test the app through Streamlit after changes so I could see how they were reflected. Rather than only verifying that the happy path worked, I included scenarios that are more likely to expose bugs, such as empty task lists, duplicate task times, recurring tasks, and overlapping schedules. This gave me confidence that the scheduling logic behaves consistently across a variety of situations and the app won't just crash.

If I had more time, I would expand my tests to include larger schedules with multiple pets and dozens of tasks to evaluate scalability. I would also test situations where the total scheduled task duration exceeds the owner's available time, as well as more complex schedules with multiple daily and weekly tasks occurring simultaneously.

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I am most satisfied with is the overall organization of my program and the visual layout through Streamlit. I separated the project into Owner, Pet, Task, and Planner classes to make the code easier to understand and maintain. I also made sure the app wasn't messy when viewed. While simple in nature, it took the user through the necessary steps they needed to schedule tasks. For example, first the user would put basic info about themselves, add a pet, assign tasks then view the schedule or filter tasks. The program doesn't seem confusing when being viewed, which I am glad to see.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had more time to add another iteration, I would improve the conflict detection to go beyond just displaying an error message. Instead, I would keep the error message but also suggest possible times where the owner could add that task if they wanted it. Maye even implement a feature where the user just inputs tasks and a time frame or time of day and the program can generate potential schedules. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned working with AI is AI is especially helpful when it comes to debugging because it can easily read over files and highlight code where the issue occurs. I think there's much more error to skip over errors when a human's doing it. I also learned that implementing the system first yourself then asking AI for help on certain steps instead of having it design the entire system reduced bugs or errors in-between. Sometimes even AI can confuse itself by overshooting the program in terms of complexity!