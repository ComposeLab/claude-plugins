---
name: python-concurrency
description: Guides writing concurrent Python code using threading and multiprocessing, with guidance on GIL implications and model selection.
version: 1.0.0
author: composeLab
triggers:
  - "Python threading"
  - "Python multiprocessing"
  - "parallel Python code"
  - "Python GIL"
  - "concurrent processing"
tags:
  - python
  - concurrency
  - threading
  - multiprocessing
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: true
---

# python-concurrency

Assists with writing concurrent Python code using threading and multiprocessing. Covers the GIL, thread safety, process-based parallelism, synchronization primitives, and choosing the right concurrency model.

## Workflow: Write Code

### Step 1: Understand the Task

Identify what the user needs: parallel computation, background tasks, shared-state coordination, or data pipeline parallelism. Determine whether the workload is CPU-bound or I/O-bound.

### Step 2: Choose the Concurrency Model

Consult [Choosing a Concurrency Model](references/choosing-concurrency-model.md) for the decision framework. The GIL makes this choice critical in Python — the wrong model wastes resources or provides no speedup.

For I/O-bound work, consider directing the user to the `python-asyncio` sibling skill, which is often more efficient than threading for network operations.

### Step 3: Implement

Consult [GIL and Execution Model](references/gil-and-execution-model.md) to understand how Python executes threads and processes.

For thread-based concurrency, consult [Threading Patterns](references/threading-patterns.md) for Thread class, ThreadPoolExecutor, daemon threads, and thread-safe patterns.

For process-based parallelism, consult [Multiprocessing Patterns](references/multiprocessing-patterns.md) for Process class, ProcessPoolExecutor, Pool, shared memory, and inter-process communication.

### Step 4: Synchronize

If threads or processes share state, consult [Synchronization Primitives](references/synchronization-primitives.md) for locks, events, semaphores, queues, and barriers.

### Step 5: Review

Verify the code avoids common pitfalls: race conditions, deadlocks, the GIL limiting CPU parallelism in threads. Present the result to the user.

## Workflow: Explain Concept

### Step 1: Identify the Topic

Determine which concurrency concept the user wants to understand. Map it to the relevant reference file.

### Step 2: Teach the Concept

Consult the appropriate reference and explain WHY the concept exists, HOW Python's execution model affects it, and WHEN to use each approach.

### Step 3: Offer Follow-up

Suggest related patterns. For async I/O questions, direct to the `python-asyncio` sibling skill.
