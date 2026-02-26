# Common Pitfalls

## Blocking the Event Loop

The most frequent asyncio mistake is calling synchronous blocking code inside a coroutine. Because the event loop runs in a single thread, any blocking call freezes all concurrent coroutines until it returns. This defeats the purpose of async programming.

Common blocking offenders include `time.sleep()`, synchronous HTTP libraries like `requests`, synchronous database drivers, CPU-heavy computation, and standard file I/O.

```python
# Wrong: blocks the entire event loop for 2 seconds.
import time

async def bad_handler():
    time.sleep(2)  # No other coroutine can run during this.
    return "done"
```

```python
# Right: use async equivalents or offload to a thread.
import asyncio

async def good_handler():
    await asyncio.sleep(2)  # Event loop runs other coroutines during this.
    return "done"

async def good_handler_blocking_lib():
    # For unavoidably synchronous code, offload to a thread.
    result = await asyncio.to_thread(blocking_function)
    return result
```

Enable asyncio debug mode (`asyncio.run(main(), debug=True)`) to get warnings when callbacks take longer than 100ms, which helps surface hidden blocking calls.

## Forgetting to Await Coroutines

Calling an `async def` function without `await` returns a coroutine object but never executes the function body. Python emits a "coroutine was never awaited" warning, but this is easy to miss, especially in larger codebases.

```python
# Wrong: fetch() is called but never executed.
async def main():
    result = fetch("https://api.example.com")  # Missing await!
    print(result)  # Prints: <coroutine object fetch at 0x...>
```

```python
# Right: await the coroutine.
async def main():
    result = await fetch("https://api.example.com")
    print(result)  # Prints the actual response.
```

This pitfall is especially dangerous in fire-and-forget scenarios where the missing `await` means the side effect (sending an email, logging an event) silently never happens. Always run with debug mode during development to catch these.

## Fire-and-Forget Tasks Getting Garbage Collected

When you create a task with `asyncio.create_task()` but do not store a reference to it, the task object may be garbage collected before it completes. This is a CPython implementation detail: if nothing references the task, the garbage collector can destroy it, and the coroutine is abandoned silently.

```python
# Wrong: task has no strong reference and may be garbage collected.
async def main():
    asyncio.create_task(send_email("user@example.com"))
    # If main() exits quickly, the task may never complete.
```

```python
# Right: keep a reference to background tasks.
_background_tasks: set[asyncio.Task] = set()

async def main():
    task = asyncio.create_task(send_email("user@example.com"))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    # Task is now protected from garbage collection.
```

The pattern of maintaining a set of background tasks with a done callback that removes them is the standard solution recommended in the Python documentation.

## Exception Handling in Gathered Tasks

`asyncio.gather()` with default settings propagates the first exception and cancels remaining tasks. This means exceptions from other tasks are lost. Using `return_exceptions=True` prevents this but changes the return type to a mix of results and exceptions that you must inspect manually.

```python
# Wrong: second task's ValueError is lost.
async def main():
    try:
        results = await asyncio.gather(
            task_that_raises_connection_error(),
            task_that_raises_value_error(),
        )
    except ConnectionError:
        print("Only this one is caught")
```

```python
# Right: use return_exceptions to capture all failures.
async def main():
    results = await asyncio.gather(
        task_that_raises_connection_error(),
        task_that_raises_value_error(),
        return_exceptions=True,
    )
    for result in results:
        if isinstance(result, Exception):
            print(f"Task failed: {result}")
        else:
            print(f"Task succeeded: {result}")
```

In Python 3.11+, prefer `TaskGroup` over `gather` for concurrent work. TaskGroup raises an `ExceptionGroup` containing all task exceptions, ensuring none are lost.

## Mixing Sync and Async Code Incorrectly

Calling `asyncio.run()` from inside a coroutine that is already running on an event loop raises `RuntimeError`. This happens when you try to "bridge" from async back to sync back to async.

```python
# Wrong: nested asyncio.run() from within async context.
async def inner():
    return "data"

def sync_helper():
    return asyncio.run(inner())  # RuntimeError if loop is running!

async def main():
    result = sync_helper()  # Crashes.
```

```python
# Right: stay async throughout or use run_in_executor for sync code.
async def main():
    result = await inner()  # Just await directly.
```

If you genuinely need to call async code from a sync function that is itself called from async code, restructure the call chain to keep everything async. As a last resort, `asyncio.run_coroutine_threadsafe()` can schedule a coroutine from a different thread onto a running loop.

## Running asyncio.run() from Async Context

This is a special case of the above. Jupyter notebooks, some web frameworks (FastAPI, Quart), and testing frameworks (pytest-asyncio) already run an event loop. Calling `asyncio.run()` in these environments fails.

```python
# Wrong in Jupyter:
asyncio.run(main())  # RuntimeError: cannot be called from a running event loop

# Right in Jupyter: just await directly.
await main()
```

For scripts that might run in both contexts, check first:

```python
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = None

if loop is None:
    asyncio.run(main())
else:
    await main()
```

## Starvation from Long-Running Coroutines

A coroutine that performs a long computation without any `await` points monopolizes the event loop. Other coroutines, timers, and I/O callbacks are all starved until the long-running coroutine yields.

```python
# Wrong: no await points in the loop, starves the event loop.
async def compute_heavy(data):
    result = []
    for item in data:  # Could be millions of items.
        result.append(expensive_transform(item))
    return result
```

```python
# Right: periodically yield control back to the event loop.
async def compute_heavy(data):
    result = []
    for i, item in enumerate(data):
        result.append(expensive_transform(item))
        if i % 1000 == 0:
            await asyncio.sleep(0)  # Yield to the event loop.
    return result
```

For truly CPU-bound work, `asyncio.sleep(0)` every N iterations is a band-aid. The proper solution is to offload the computation to a process pool via `loop.run_in_executor()` with a `ProcessPoolExecutor`, or use the `python-concurrency` sibling skill for guidance on multiprocessing.

## Not Cleaning Up Resources

Async resources like database connections, HTTP sessions, and file handles need explicit async cleanup. Relying on garbage collection or `__del__` does not work reliably because finalizers cannot run coroutines.

```python
# Wrong: session is never closed, leaking connections.
async def fetch_all(urls):
    session = aiohttp.ClientSession()
    results = []
    for url in urls:
        async with session.get(url) as resp:
            results.append(await resp.text())
    return results
    # session.close() is never called!
```

```python
# Right: use async with to guarantee cleanup.
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        results = []
        for url in urls:
            async with session.get(url) as resp:
                results.append(await resp.text())
        return results
    # session is automatically closed here.
```

The rule is simple: if a resource has an `async close()`, `aclose()`, or supports `async with`, always use the context manager form. This guarantees cleanup even when exceptions occur.
