# Embedded Systems & RTOS Study Notes
**Date:** March 14, 2026  
**Subject:** Core Fundamentals & FreeRTOS Introduction

---

## I. General Programming Concepts

### 1. Macros (`#define`)
* **Definition:** A rule or pattern that automatically expands a single instruction into a set of statements during the "Preprocessing" stage (before the compiler runs).
* **Analogy:** A **"Find and Replace"** tool. If you `#define PI 3.14`, the computer literally replaces the word "PI" with "3.14" everywhere in your code before it runs.
* **Function-like macros:** Resemble functions, allowing parameter passing, such as `#define SQUARE(x) ((x) * (x))`.
* **Pros:** Efficiency; improves speed by avoiding function call overhead. Helps automate repetitive structures.
* **Cons:** No type safety (the computer doesn't check if it's an `int` or a `float`), making bugs harder to find. Difficult to debug because errors point to the expanded code, not your original macro.

### 2. .ino vs .cpp
* **The Reality:** `.ino` is just `.cpp` with "training wheels."
* **What the IDE hides:** It automatically adds `#include <Arduino.h>`, generates function prototypes, and wraps your `setup()` and `loop()` inside a hidden `main()` function.
* **Why it exists:** To let beginners focus on logic without worrying about the strict boilerplate structure of professional C++. Under the hood, it is fed to a standard C++ compiler.

---

## II. Hardware & Communication

### 1. DMA (Direct Memory Access)
* **Definition:** A dedicated hardware assistant inside the microcontroller whose only job is moving data between peripherals and RAM without involving the CPU.
* **Analogy:** The **Conveyor Belt**.
    * **Without DMA:** The CPU has to stop its main job, read a byte, write it to RAM, and repeat 1,000 times.
    * **With DMA:** The CPU tells the DMA to grab 1,000 bytes and put them in a folder, then send an interrupt when finished. The CPU can keep doing complex math in the meantime.
* **Key Value:** Saves massive amounts of processing power.

### 2. Communication Protocols

| Protocol | Wires | Speed | Best Use Case |
| :--- | :---: | :---: | :--- |
| **I2C** | 2 | Slow/Medium | Connecting many different sensors using only 2 wires. Every device gets an address. |
| **SPI** | 4 | Very Fast | High-bandwidth data like SD Cards or color displays. Full-duplex (sends and receives simultaneously). |
| **UART** | 2 | Variable | Simple, point-to-point communication (TX and RX). Asynchronous (no clock wire). |

---

## III. CPU Architecture: Cores vs. Threads

* **Core (Hardware):** The actual physical silicon brain that executes instructions. An 8-core processor can execute 8 different math problems at the exact same physical microsecond. 
* **Thread/Task (Software):** A sequence of software instructions. 
* **The RTOS Magic:** Most microcontrollers only have **1 Core**. FreeRTOS uses a **Scheduler** to run multiple **Threads (Tasks)**. It switches between them so incredibly fast (e.g., 1 millisecond per task) that the human brain perceives them as running at the same time.

---

## IV. FreeRTOS Essentials

### 1. Task Management
* **Independence:** Each Task thinks it owns the whole CPU. It has no coincidental dependency on other tasks.
* **The Scheduler:** The "invisible hand" responsible for repeatedly starting and stopping each task. A task has no knowledge of the scheduler's activity.
* **Context Switching:** When a task is swapped out, its context (register values, variables) is saved to its own private **Stack**. When swapped back in, it is exactly restored.

### 2. The Cheat Sheet
* **Scheduling Types:** * *Pre-emptive:* A high-priority task instantly interrupts a low-priority one.
    * *Co-operative:* Tasks politely wait their turn (rarely used now).
* **Deterministic Execution:** FreeRTOS guarantees it will never do unpredictable, time-wasting operations (like searching a linked list) from inside an interrupt. Timing is strictly guaranteed.
* **Zero-Waste Waiting:** Blocked tasks and software timers use absolutely zero CPU power while waiting.
* **Queues are Core:** Queues are the primary, highly optimized way to pass data around. They combine simplicity with flexibility and are designed to use tiny amounts of RAM.
