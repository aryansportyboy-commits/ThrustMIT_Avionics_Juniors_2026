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

## Inter-Task Communication & Synchronization

When multiple tasks need to talk to each other or share hardware, they use these FreeRTOS OS primitives to avoid data corruption.

### 1. Queues (Passing Data)
* **What it is:** A safe, First-In-First-Out (FIFO) buffer used to pass actual data (like an array of sensor readings) from one task to another.
* **Why we use it:** Prevents data corruption. It stops Task B from reading a variable while Task A is only halfway through writing to it.

### 2. Semaphores & Mutexes (Keys & Flags)
* **Mutex (Bathroom Key):** Protects a shared resource. If two tasks share one I2C bus, a Mutex ensures only one task can talk on the wires at a time.
* **Binary Semaphore (The Flare Gun):** Used for signaling. A hardware interrupt can "give" a semaphore to instantly wake up a high-priority task that is waiting for an event.

### 3. Event Groups (The Checklist)
* **What it is:** A set of boolean flags (bits). 
* **Why we use it:** Allows a task to wait in the Blocked state until *multiple* conditions are met at the same time (e.g., wait until Apogee is True AND Timer > 10s).

### 4. Task Notifications (The Direct DM)
* **What it is:** A lightweight way for a task to signal another specific task directly.
* **Why we use it:** It is significantly faster and uses less RAM than Queues or Semaphores, but is slightly less flexible. Best for simple "wake up!" signals.

## Task Priorities & Scheduling Rules

### 1. The Priority Scale
* **Higher Number = Higher Priority:** In FreeRTOS, priority 10 beats priority 1. 
* **Priority 0 (The Idle Task):** The lowest possible priority. The OS automatically creates an "Idle Task" here that just sweeps up deleted memory and wastes time when no other tasks want to run.
* **The Golden Rule of the Scheduler:** The task in the Running state is **always** the highest-priority task that is able to run. 

### 2. Time Slicing (Round Robin)
* **What happens with ties?** If two tasks share the exact same priority (e.g., both are Priority 2) and both are Ready, the Scheduler automatically shares the CPU. It gives them alternating slices of time (usually 1 millisecond ticks).

### 3. RAM Efficiency & Configuration
* **configMAX_PRIORITIES:** This is a setting in `FreeRTOSConfig.h`. It defines the maximum allowed priority level. 
* **The Best Practice:** Keep this number as small as possible for your specific project. Making the max priority unnecessarily high wastes RAM.

## Scheduling Policies & Multi-Core Architecture

### 1. The Default FreeRTOS Policy
The official default algorithm is **Fixed-Priority Preemptive Scheduling with Round-Robin Time-Slicing**:
* **Fixed Priority:** The programmer sets the priority; the OS doesn't randomly change it.
* **Preemptive:** Highest priority always gets the CPU.
* **Round-Robin / Time-Sliced:** Equal priority tasks take turns sharing the CPU via 1-millisecond slices.

### 2. The Danger of "Task Starvation"
* **The Problem:** If a high-priority task uses a continuous polling loop (e.g., `while(1)` checking a variable) instead of an OS primitive, it will NEVER enter the Blocked state. Lower-priority tasks will be permanently starved of CPU time and your system will freeze.
* **The Solution:** Always make tasks **event-driven**. High-priority tasks should Block (using Queues, Semaphores, or `vTaskDelay`) while waiting for data.

### 3. Multi-Core RTOS (AMP vs. SMP)
When running on modern multi-core chips (like the ESP32 or RP2040):
* **AMP (Asymmetric Multiprocessing):** Each core runs its own independent, separate instance of FreeRTOS.
* **SMP (Symmetric Multiprocessing):** ONE instance of FreeRTOS acts as the master brain, scheduling tasks across ALL available cores simultaneously.

### 4. SMP Quirk & Core Affinity
* **The Quirk:** In SMP, a high-priority task and a medium-priority task can run at the exact same physical time (on different cores). You can no longer assume a lower-priority task is paused just because a higher one is running.
* **Core Affinity (`configUSE_CORE_AFFINITY`):** A setting that allows you to "pin" a specific task to a specific physical core to prevent timing bugs or data collisions.

## Writing a FreeRTOS Task in C

### 1. The Core Structure
* **Infinite Loop:** Every task is implemented as a continuous loop (`for(;;)` or `while(1)`).
* **Never Return:** A task function must never reach its end bracket or use `return`. 
* **How to Exit:** If a task must die, it must call `vTaskDelete(NULL)` to clean up its memory safely.

### 2. Event-Driven Design
* **Don't Hog the CPU:** Inside the infinite loop, you must use an OS-blocking function (like `vTaskDelay()` or waiting on a Queue). This forces the task into the "Blocked" state so lower-priority tasks can run.
* **Macros:** You can ignore the `portTASK_FUNCTION` macros. Standard C void pointers (`void vMyTask(void *pvParameters)`) are the modern standard.
### 3. Practical Example: ESP32 Dual-Core Architecture
This template demonstrates how to run the BMP388 sensor on Core 0, the MPU6050 sensor on Core 0, and a higher-priority Apogee Math task on Core 1 using FreeRTOS.



```c
#include <Arduino.h>

TaskHandle_t BMPTaskHandle;
TaskHandle_t MPUTaskHandle;
TaskHandle_t ThirdTaskHandle;

void vBMPTask(void *pvParameters) {
    for(;;) {
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void vMPUTask(void *pvParameters) {
    for(;;) {
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

void vThirdTask(void *pvParameters) {
    for(;;) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void setup() {
    xTaskCreatePinnedToCore(vBMPTask, "BMP_Task", 2048, NULL, 1, &BMPTaskHandle, 0);
    xTaskCreatePinnedToCore(vMPUTask, "MPU_Task", 2048, NULL, 1, &MPUTaskHandle, 0);
    xTaskCreatePinnedToCore(vThirdTask, "Third_Task", 4096, NULL, 2, &ThirdTaskHandle, 1);
}

void loop() {
}

```
### 📝 Personal Note (End of Theory)
For theory today, I am stopping at implementing a task section for FreeRTOS. I will now work on a practical mini-project I've thought of: using a single ESP32 to read a BMP and MPU continuously via time slicing.
