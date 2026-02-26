# Async Patterns

## Producer-Consumer with asyncio.Queue

The producer-consumer pattern decouples data generation from data processing, allowing both sides to run at their own pace. `asyncio.Queue` is the async-safe channel between them. Unlike `queue.Queue` from the standard library, `asyncio.Queue` uses coroutine-based `put()` and `get()` that yield to the event loop instead of blocking the thread.

```python
import asyncio

async def producer(queue: asyncio.Queue, items: list[str]):
    for item in items:
        await asyncio.sleep(0.1)  # simulate producing data
        await queue.put(item)
        print(f"Produced: {item}")
    # Signal completion with a sentinel value.
    await queue.put(None)

async def consumer(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        await asyncio.sleep(0.3)  # simulate processing
        print(f"Consumed: {item}")
        queue.task_done()

async def main():
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=10)
    await asyncio.gather(
        producer(queue, ["a", "b", "c", "d"]),
        consumer(queue),
    )

asyncio.run(main())
```

For multiple consumers, send one sentinel per consumer or use `queue.join()` to wait until all items are processed, then cancel the consumer tasks.

## Semaphore-Based Rate Limiting

`asyncio.Semaphore` limits how many coroutines can enter a section of code concurrently. This is essential when hitting APIs with rate limits or when you need to bound resource consumption (database connections, file handles).

```python
import asyncio

async def fetch_with_limit(sem: asyncio.Semaphore, url: str) -> str:
    async with sem:
        print(f"Fetching {url}")
        await asyncio.sleep(1)  # simulate HTTP request
        return f"Data from {url}"

async def main():
    sem = asyncio.Semaphore(5)  # At most 5 concurrent requests.
    urls = [f"https://api.example.com/{i}" for i in range(20)]

    tasks = [fetch_with_limit(sem, url) for url in urls]
    results = await asyncio.gather(*tasks)
    print(f"Fetched {len(results)} URLs")

asyncio.run(main())
```

The semaphore acts as a gate: when 5 coroutines are inside the `async with` block, the 6th will suspend at `async with sem` until one of the active ones exits. This naturally throttles throughput without complex scheduling logic.

## Timeout Patterns

### asyncio.timeout (Python 3.11+)

The `asyncio.timeout()` context manager applies a deadline to an entire block of operations. If the block does not complete within the allotted time, all tasks inside are cancelled and `TimeoutError` is raised.

```python
import asyncio

async def main():
    try:
        async with asyncio.timeout(5.0):
            data = await fetch_data()
            result = await process_data(data)
            await save_result(result)
    except TimeoutError:
        print("The entire operation took longer than 5 seconds")

asyncio.run(main())
```

### asyncio.timeout_at (Python 3.11+)

For absolute deadlines, `asyncio.timeout_at()` accepts a loop clock timestamp rather than a relative delay. This is useful when you have a hard deadline computed from another event.

```python
async def main():
    loop = asyncio.get_running_loop()
    deadline = loop.time() + 10.0  # 10 seconds from now

    try:
        async with asyncio.timeout_at(deadline):
            await long_running_operation()
    except TimeoutError:
        print("Deadline exceeded")
```

## Async Retry with Exponential Backoff

Network operations fail transiently. A retry pattern with exponential backoff handles this gracefully. The key is to increase the wait time between retries so you do not overwhelm the target service during outages.

```python
import asyncio
import random

async def fetch_with_retry(url: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries + 1):
        try:
            return await fetch(url)
        except ConnectionError:
            if attempt == max_retries:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Retry {attempt + 1} after {wait:.1f}s")
            await asyncio.sleep(wait)
    raise RuntimeError("Unreachable")
```

Adding jitter (the `random.uniform` part) prevents thundering herd problems where many clients retry at the same instant after a shared outage.

## Fire-and-Forget (Safe Way)

Sometimes you want to launch a coroutine without awaiting its result (logging, metrics, non-critical notifications). The danger is that an unawaited task can be garbage collected silently, losing exceptions and potentially the work itself. The safe approach is to keep a reference to the task and attach an error callback.

```python
import asyncio

_background_tasks: set[asyncio.Task] = set()

def fire_and_forget(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

async def send_analytics(event: str):
    await asyncio.sleep(0.5)
    print(f"Analytics sent: {event}")

async def main():
    fire_and_forget(send_analytics("page_view"))
    # Continue doing other work without waiting for analytics.
    await asyncio.sleep(1)

asyncio.run(main())
```

The set `_background_tasks` holds strong references so tasks are not garbage collected. The `add_done_callback` removes the reference once the task completes, preventing a memory leak.

## Running Blocking Code in an Executor

When you must call synchronous blocking code from async context (legacy libraries, CPU-heavy functions, file system operations), use `loop.run_in_executor()` to offload the work to a thread pool or process pool. This keeps the event loop responsive.

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def blocking_io():
    """A synchronous function that performs blocking I/O."""
    import time
    time.sleep(2)
    return "done"

async def main():
    loop = asyncio.get_running_loop()

    # Run in the default thread pool executor.
    result = await loop.run_in_executor(None, blocking_io)
    print(result)

    # Or use a custom executor for more control.
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, blocking_io)
        print(result)

asyncio.run(main())
```

The `asyncio.to_thread()` function (Python 3.9+) is a simpler wrapper for the common case of offloading to a thread:

```python
async def main():
    result = await asyncio.to_thread(blocking_io)
    print(result)
```

## Combining Asyncio with Synchronous Libraries

Some situations require calling async code from synchronous contexts (e.g., integrating asyncio into a Django view or a CLI tool). If no event loop is running, use `asyncio.run()`. If a loop is already running (rare in application code, common in notebooks), you may need `nest_asyncio` or restructuring.

```python
# Synchronous entry point calling async code.
import asyncio

def sync_api_call():
    return asyncio.run(async_fetch_data())

# For libraries like Flask that are sync by default:
def flask_handler():
    data = asyncio.run(gather_from_multiple_apis())
    return jsonify(data)
```

The reverse direction (calling sync from async) always uses `run_in_executor` or `asyncio.to_thread` as shown above. Never call synchronous blocking functions directly in async code.
