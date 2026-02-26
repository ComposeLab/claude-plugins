# Choosing a Concurrency Model

## The Core Decision

Python offers three concurrency models, and the GIL makes choosing correctly more consequential than in most languages. A wrong choice does not just result in suboptimal code — it can produce code that is slower than the sequential version while being harder to debug.

The primary factor is whether the workload is CPU-bound or I/O-bound. CPU-bound work spends time computing. I/O-bound work spends time waiting for external systems (network, disk, databases). Most real applications have a mix, but one side usually dominates.

## Decision Framework

**I/O-bound work** (network calls, file I/O, database queries): Use `asyncio` as the first choice. It handles thousands of concurrent connections on a single thread with minimal overhead. Use `threading` when you need to integrate with synchronous libraries that cannot be made async, or when the concurrency level is modest (tens of tasks, not thousands).

**CPU-bound work** (number crunching, image processing, data transformation): Use `multiprocessing` or `ProcessPoolExecutor`. These bypass the GIL by running work in separate processes. Threading provides no speedup for CPU-bound Python code.

**Mixed workloads**: Combine models. A common architecture uses `asyncio` for the I/O layer and dispatches CPU-heavy subtasks to a `ProcessPoolExecutor` via `loop.run_in_executor()`.

## Comparison Table

| Aspect | asyncio | threading | multiprocessing |
|--------|---------|-----------|-----------------|
| Best for | High-concurrency I/O | Moderate I/O with sync libraries | CPU-bound computation |
| GIL impact | N/A (single thread) | Limits CPU parallelism | Bypassed (separate processes) |
| Memory overhead | Very low | Low (shared memory) | High (separate memory per process) |
| Data sharing | Trivial (single thread) | Shared memory (needs locks) | Requires IPC or shared memory |
| Startup cost | Negligible | Low | High (process creation) |
| Max concurrency | Thousands+ | Hundreds | Number of CPU cores |
| Debugging | Moderate (async stack traces) | Hard (race conditions) | Moderate (isolated processes) |
| Library support | Growing (aiohttp, asyncpg) | Universal | Universal |

## Real-World Scenarios

### Web Scraping

Web scraping is I/O-bound — most time is spent waiting for HTTP responses. `asyncio` with `aiohttp` is the ideal choice because it can manage hundreds of concurrent requests with minimal resource usage.

```python
import asyncio
import aiohttp

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [f"https://example.com/page/{i}" for i in range(100)]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    print(f"Fetched {len(results)} pages")

asyncio.run(main())
```

If the scraping library is synchronous (like `requests`), fall back to `ThreadPoolExecutor`.

### Image Processing

Image processing is CPU-bound — pixels need to be computed. Use `ProcessPoolExecutor` to distribute work across cores.

```python
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
import os

def resize_image(path):
    img = Image.open(path)
    img = img.resize((800, 600))
    output = path.replace(".jpg", "_resized.jpg")
    img.save(output)
    return output

if __name__ == "__main__":
    image_paths = [f"photo_{i}.jpg" for i in range(100)]
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(resize_image, image_paths))
    print(f"Resized {len(results)} images")
```

### Database Operations

Database queries are I/O-bound. If using an async driver (like `asyncpg` for PostgreSQL), use `asyncio`. If using a synchronous driver (like `psycopg2`), use `ThreadPoolExecutor` — the GIL is released during the network wait, so threads work well.

```python
from concurrent.futures import ThreadPoolExecutor
import psycopg2

def query_db(query):
    conn = psycopg2.connect("dbname=mydb")
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    return result

queries = [f"SELECT * FROM users WHERE id = {i}" for i in range(50)]

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(query_db, queries))
```

## The concurrent.futures Unified API

The `concurrent.futures` module provides `ThreadPoolExecutor` and `ProcessPoolExecutor` with identical interfaces. This makes it easy to prototype with threads and switch to processes (or vice versa) by changing a single line.

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def compute(n):
    return sum(i * i for i in range(n))

# Switch between these by changing only the executor class:
# executor_class = ThreadPoolExecutor  # For I/O-bound
executor_class = ProcessPoolExecutor    # For CPU-bound

if __name__ == "__main__":
    with executor_class(max_workers=4) as executor:
        results = list(executor.map(compute, [1_000_000] * 8))
```

This is valuable during development when you are not yet sure which model is faster. Benchmark both and keep the winner.

## Overhead Considerations

Process creation is expensive — spawning a process can take 50-100ms on some systems. For tasks that take less than a few milliseconds each, the overhead of multiprocessing can exceed the computation time. In those cases, increase the work per task (batch items) or use threading if the work is I/O-bound.

Thread creation is cheaper but not free. Creating thousands of short-lived threads causes significant overhead. Use a thread pool to reuse threads across tasks.

Asyncio coroutines have the lowest overhead — creating a coroutine is as cheap as creating a small Python object. This is why asyncio scales to thousands of concurrent tasks where threading cannot.

## Scaling Considerations

Threading scales well to hundreds of concurrent I/O tasks but degrades beyond that due to OS thread scheduling overhead and memory usage (each thread uses about 8MB of stack by default on Linux).

Multiprocessing scales to the number of CPU cores. Beyond that, additional processes compete for CPU time and the overhead of process management outweighs any benefit.

Asyncio scales to tens of thousands of concurrent tasks on a single thread, limited mainly by available memory and the event loop's ability to process callbacks.

For workloads that exceed the scaling limits of a single machine, consider distributed task systems like Celery, Dask, or Ray, which build on these primitives but distribute work across multiple machines.
