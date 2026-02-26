# Tasks and Concurrency

## asyncio.create_task()

A coroutine on its own does not run concurrently. It only runs when awaited, and the awaiting coroutine is suspended until it completes. To run coroutines concurrently, you wrap them in tasks. `asyncio.create_task()` schedules a coroutine to run on the event loop and returns a `Task` object immediately, without waiting for the coroutine to finish. The task starts executing at the next opportunity the event loop gets.

```python
import asyncio

async def fetch(url: str) -> str:
    print(f"Fetching {url}")
    await asyncio.sleep(1)  # simulate network I/O
    return f"Data from {url}"

async def main():
    # These two fetches run concurrently because they are tasks.
    task1 = asyncio.create_task(fetch("https://api.example.com/a"))
    task2 = asyncio.create_task(fetch("https://api.example.com/b"))

    # Await both results. Total time is ~1s, not ~2s.
    result1 = await task1
    result2 = await task2
    print(result1, result2)

asyncio.run(main())
```

Tasks must be created from within a running event loop. Calling `create_task()` outside of an async context raises `RuntimeError`.

## TaskGroup (Python 3.11+)

`asyncio.TaskGroup` provides structured concurrency: all tasks created within the group are guaranteed to complete (or be cancelled) before the `async with` block exits. If any task raises an exception, the remaining tasks are cancelled and the exception group is re-raised. This eliminates the common problem of orphaned tasks.

```python
import asyncio

async def process(item: int) -> int:
    await asyncio.sleep(0.5)
    return item * 2

async def main():
    results = []
    async with asyncio.TaskGroup() as tg:
        for i in range(5):
            task = tg.create_task(process(i))
            results.append(task)

    # All tasks are done here. Access results safely.
    print([t.result() for t in results])

asyncio.run(main())
```

TaskGroup is the preferred approach for concurrent work in Python 3.11+ because it enforces cleanup. If one task fails, the group cancels sibling tasks and raises an `ExceptionGroup` containing all failures. Handle these with `except*` syntax.

```python
async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(might_fail())
            tg.create_task(might_also_fail())
    except* ValueError as eg:
        for exc in eg.exceptions:
            print(f"ValueError occurred: {exc}")
    except* OSError as eg:
        for exc in eg.exceptions:
            print(f"OSError occurred: {exc}")
```

## asyncio.gather()

`asyncio.gather()` runs multiple awaitables concurrently and returns their results as a list in the same order they were passed. It predates TaskGroup and remains useful for simple concurrent execution where structured cleanup is not critical.

```python
async def main():
    results = await asyncio.gather(
        fetch("https://api.example.com/a"),
        fetch("https://api.example.com/b"),
        fetch("https://api.example.com/c"),
    )
    # results is a list of three return values, in order.
    print(results)
```

The `return_exceptions=True` parameter causes exceptions to be returned as values in the results list rather than propagated. Without it, the first exception cancels the gather and propagates immediately. With it, all awaitables run to completion regardless of individual failures.

```python
async def main():
    results = await asyncio.gather(
        fetch("https://good.example.com"),
        fetch("https://bad.example.com"),  # raises ConnectionError
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"Task failed: {r}")
        else:
            print(f"Task succeeded: {r}")
```

## asyncio.wait()

`asyncio.wait()` gives finer control over task completion. It returns two sets: `done` and `pending`. The `return_when` parameter controls when it returns.

```python
async def main():
    tasks = [asyncio.create_task(fetch(url)) for url in urls]

    # Return as soon as the first task completes.
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in done:
        print(task.result())

    # Cancel remaining tasks if you only needed the first result.
    for task in pending:
        task.cancel()
```

`FIRST_COMPLETED` is useful for racing multiple strategies (e.g., try two API endpoints and use whichever responds first). `ALL_COMPLETED` waits for everything, similar to `gather` but returning sets instead of an ordered list. `FIRST_EXCEPTION` returns when any task raises, allowing early error detection.

## asyncio.wait_for() and Timeouts

`asyncio.wait_for()` wraps a single awaitable with a timeout. If the awaitable does not complete in time, it is cancelled and `asyncio.TimeoutError` is raised.

```python
async def main():
    try:
        result = await asyncio.wait_for(fetch("https://slow.example.com"), timeout=5.0)
    except asyncio.TimeoutError:
        print("Request timed out after 5 seconds")
```

For Python 3.11+, the `asyncio.timeout()` context manager provides a cleaner approach for timing out a block of operations. See the async-patterns reference for details.

## Task Cancellation

Any task can be cancelled by calling `task.cancel()`. This injects a `CancelledError` into the task at its next `await` point. The task can catch `CancelledError` to perform cleanup before re-raising it, but suppressing it entirely is discouraged because it breaks the cancellation contract.

```python
async def graceful_worker():
    try:
        while True:
            await asyncio.sleep(1)
            print("Working...")
    except asyncio.CancelledError:
        print("Cleaning up before cancellation...")
        raise  # Always re-raise CancelledError.
```

## Shielding Tasks

`asyncio.shield()` protects an awaitable from cancellation. If the outer task is cancelled, the shielded inner coroutine continues running. This is useful for operations that must not be interrupted, like database commits.

```python
async def critical_save(data):
    await db.commit(data)

async def handler(data):
    # Even if handler is cancelled, the save will complete.
    await asyncio.shield(critical_save(data))
```

Note that shield only protects from outer cancellation. If the shielded coroutine itself fails, the exception propagates normally.

## Task Naming

Naming tasks aids debugging by making log output and stack traces more readable. Pass the `name` parameter to `create_task()` or `TaskGroup.create_task()`.

```python
task = asyncio.create_task(fetch(url), name=f"fetch-{url}")
print(task.get_name())  # "fetch-https://api.example.com/a"
```

In production systems with many concurrent tasks, meaningful names make it far easier to identify which task is stuck, slow, or failing when inspecting logs or debugging with `asyncio.all_tasks()`.
