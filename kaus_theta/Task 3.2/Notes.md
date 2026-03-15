## Tasks vs. Co-Routines



### 1. Tasks (The Modern Standard)
* **How they work:** Structured as independent mini-programs. The RTOS Scheduler swaps them in and out rapidly.
* **Memory (RAM):** Every single task gets its own private **Stack** to save its context (variables, registers) when paused. This uses more RAM but is much safer.
* **Preemption:** Fully supported. A high-priority task can instantly interrupt a lower-priority one.
* **Verdict:** Simple, powerful, and what you will use 99% of the time.

### 2. Co-Routines (The Legacy Option)
* **How they work:** Conceptually similar to tasks, but heavily restricted to save memory.
* **Memory (RAM):** All co-routines share a **Single Stack**. This saves massive amounts of RAM but means they have to cooperate to avoid overwriting each other's data.
* **Scheduling:** Cooperative only. They cannot preempt each other (though a Task can preempt a Co-routine).
* **Verdict:** The official docs say they are "very rarely used in the field these days." Ignore them unless you are working on a severely memory-constrained legacy chip.

  ## The 4 States of a FreeRTOS Task

Because a single-core microcontroller can only execute one instruction at a time, FreeRTOS manages multiple tasks by rapidly shifting them between these four states:

### 1. Running
* **What it is:** The task is actively utilizing the CPU right now.
* **The Rule:** On a single-core processor, only **one** task can be in the Running state at any given microsecond.

### 2. Ready
* **What it is:** The task is perfectly able to run, but it is waiting in line. 
* **Why:** A different task of equal or higher priority is currently occupying the Running state.

### 3. Blocked (The Most Important State)
* **What it is:** The task is waiting for an event (e.g., waiting 10ms using `vTaskDelay()`, or waiting for data to arrive in a Queue). 
* **CPU Usage:** **0%**. The task gives up the CPU entirely so other tasks can run.
* **The Safety Net (Timeout):** Tasks in the Blocked state usually have a strict timeout. If the event doesn't happen in time, the task unblocks automatically to prevent the system from freezing.

### 4. Suspended
* **What it is:** A manual "deep sleep" state. 
* **How it differs from Blocked:** There is no timeout. A suspended task will wait forever until another task explicitly wakes it up.
* **API Calls:** Entered via `vTaskSuspend()` and exited via `xTaskResume()`.
