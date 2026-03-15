## V. Tasks vs. Co-Routines



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
