# Event Loop and Coroutines

## What Is a Coroutine

A coroutine is a function defined with `async def` that can suspend its execution at `await` points, yielding control back to the event loop. Unlike regular functions that run to completion once called, coroutines participate in cooperative multitasking: they voluntarily pause when waiting for I/O, allowing other coroutines to run in the meantime. Calling an `async def` function does not execute its body immediately. Instead, it returns a coroutine object that must be awaited or scheduled onto the event loop.

```python
import asyncio

async def greet(name: str) -> str:
    """A simple coroutine that returns a greeting."""
    await asyncio.sleep(0.1)  # simulate I/O delay
    return f"Hello, {name}"

# Calling greet() returns a coroutine object, not the string.
# You must await it or pass it to asyncio.run().
```

## The Event Loop

The event loop is the central scheduler in asyncio. It runs in a single thread and cycles through registered coroutines, resuming each one when its awaited I/O operation completes. This single-threaded cooperative model avoids the complexity of locks and race conditions found in threaded code, at the cost of requiring that no individual coroutine blocks for a long time.

The loop maintains internal queues of ready-to-run callbacks, pending I/O watchers, and scheduled timers. When a coroutine hits an `await`, the loop stores its continuation and moves on to the next ready coroutine. When the awaited resource becomes available (socket data arrives, a timer fires), the loop marks that coroutine as ready again.

## asyncio.run() as Entry Point

`asyncio.run()` is the standard way to start an async program. It creates a new event loop, runs the given coroutine until it completes, and then shuts down the loop and all associated resources. It should be called once at the top level of your program.

```python
import asyncio

async def main():
    result = await greet("World")
    print(result)

# Entry point: creates loop, runs main(), cleans up.
asyncio.run(main())
```

`asyncio.run()` raises `RuntimeError` if called from within a running event loop. This commonly happens in Jupyter notebooks or frameworks that already manage their own loop. In those environments, you should `await` the coroutine directly instead.

## Loop Lifecycle

The event loop progresses through a clear lifecycle: creation, running, and shutdown. During shutdown, `asyncio.run()` cancels all outstanding tasks, waits for them to handle cancellation, closes async generators, and shuts down the default executor. This cleanup is why `asyncio.run()` is preferred over manually managing the loop.

```python
import asyncio

async def worker(n: int):
    print(f"Worker {n} starting")
    await asyncio.sleep(1)
    print(f"Worker {n} done")

async def main():
    # Both workers run concurrently within the same loop.
    async with asyncio.TaskGroup() as tg:
        tg.create_task(worker(1))
        tg.create_task(worker(2))
    print("All workers finished")

asyncio.run(main())
```

## Running in an Existing Loop

When you need to schedule work onto an already-running loop from synchronous code (for example, a callback-based library integration), use `asyncio.get_running_loop()` to get the current loop and `loop.create_task()` or `asyncio.ensure_future()` to schedule coroutines. Avoid `asyncio.get_event_loop()` in modern Python because it has confusing deprecation-era behavior around implicit loop creation.

```python
import asyncio

async def background_work():
    loop = asyncio.get_running_loop()
    # Schedule a coroutine on the running loop from within async code.
    task = loop.create_task(some_coroutine())
    return await task
```

## Debug Mode

Running asyncio in debug mode surfaces common mistakes like coroutines that were never awaited and callbacks that take too long. Enable it by passing `debug=True` to `asyncio.run()` or by setting the `PYTHONASYNCIODEBUG=1` environment variable.

```python
# Debug mode warns about slow callbacks and unawaited coroutines.
asyncio.run(main(), debug=True)
```

In debug mode, the event loop logs warnings when a callback or coroutine takes longer than 100ms without yielding. This helps identify blocking calls that should be offloaded to an executor.

## asyncio.sleep vs time.sleep

`asyncio.sleep()` is a coroutine that yields control back to the event loop for the specified duration. Other coroutines can run while one is sleeping. `time.sleep()` is a blocking call that freezes the entire thread, including the event loop. Never use `time.sleep()` in async code.

```python
import asyncio
import time

async def wrong():
    time.sleep(5)  # Blocks the entire event loop for 5 seconds.

async def right():
    await asyncio.sleep(5)  # Other coroutines run during this wait.
```

The difference is fundamental: `asyncio.sleep` cooperates with the event loop, while `time.sleep` monopolizes the thread. Any synchronous blocking call (file I/O, network calls via `requests`, heavy computation) has the same problem as `time.sleep` and should be offloaded to an executor or replaced with an async equivalent.

## asyncio.sleep(0)

Calling `await asyncio.sleep(0)` is an explicit yield point. It does not actually wait but allows the event loop to run other pending callbacks and coroutines. This is useful in long-running loops to prevent starvation.

```python
async def process_items(items):
    for i, item in enumerate(items):
        do_some_work(item)
        if i % 100 == 0:
            await asyncio.sleep(0)  # Let other coroutines run.
```
