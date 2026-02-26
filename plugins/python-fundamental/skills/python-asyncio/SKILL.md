---
name: python-asyncio
description: Guides writing async Python code using asyncio including coroutines, tasks, TaskGroup, and common async patterns.
version: 1.0.0
author: composeLab
triggers:
  - "write async Python code"
  - "use asyncio"
  - "create async tasks"
  - "async await patterns"
  - "Python coroutines"
tags:
  - python
  - async
  - concurrency
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: true
---

# python-asyncio

Assists with writing async Python code using the asyncio library. Covers coroutines, tasks, TaskGroup, async context managers, async iteration, and common pitfalls.

## Workflow: Write Code

### Step 1: Understand the Task

Identify what the user needs: an async function, concurrent task execution, an async server, data pipeline, or a combination. Clarify whether the task is I/O-bound (good fit for asyncio) or CPU-bound (direct to `python-concurrency` sibling skill).

### Step 2: Design the Async Structure

Consult [Event Loop and Coroutines](references/event-loop-and-coroutines.md) for the fundamentals of async/await, event loop lifecycle, and asyncio.run().

For running multiple operations concurrently, consult [Tasks and Concurrency](references/tasks-and-concurrency.md) for asyncio.create_task, TaskGroup, gather, and wait patterns.

### Step 3: Apply Patterns

Consult [Async Patterns](references/async-patterns.md) for producer-consumer queues, semaphore-based rate limiting, timeout handling, and async retry patterns.

For async resource management and streaming, consult [Async Context and Iteration](references/async-context-and-iteration.md) for async with, async for, and async generator patterns.

### Step 4: Avoid Pitfalls

Consult [Common Pitfalls](references/common-pitfalls.md) to verify the code avoids blocking calls in async context, fire-and-forget task bugs, and other common mistakes.

### Step 5: Review

Verify all coroutines are awaited, resources are properly cleaned up with async context managers, and error handling covers task cancellation. Present the result to the user.

For GIL context and CPU-bound work, direct the user to the `python-concurrency` sibling skill which covers choosing the right concurrency model.

## Workflow: Explain Concept

### Step 1: Identify the Topic

Determine which async concept the user wants to understand. Map it to the relevant reference file.

### Step 2: Teach the Concept

Consult the appropriate reference and explain WHY async exists (cooperative multitasking for I/O-bound work), HOW the event loop schedules coroutines, and WHEN to use async vs threading vs multiprocessing.

### Step 3: Offer Follow-up

Suggest related async patterns or direct to the `python-concurrency` skill for CPU-bound or mixed workloads.
