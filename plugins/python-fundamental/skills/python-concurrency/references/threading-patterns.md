# Threading Patterns

## threading.Thread Basics

The `threading.Thread` class is the fundamental building block for thread-based concurrency. Each Thread object represents an OS-level thread managed by the operating system's scheduler. Threads share the same memory space as the main process, which makes data sharing easy but requires care to avoid race conditions.

```python
import threading

def worker(name, count):
    for i in range(count):
        print(f"{name}: step {i}")

# Create and start threads
t1 = threading.Thread(target=worker, args=("Alice", 3))
t2 = threading.Thread(target=worker, args=("Bob", 3))
t1.start()
t2.start()

# Wait for both threads to finish
t1.join()
t2.join()
print("Both threads complete.")
```

The `target` parameter takes a callable, and `args` passes positional arguments to it. Calling `start()` begins execution in a new thread. Calling `join()` blocks the calling thread until the target thread finishes. You can pass a `timeout` to `join()` to avoid blocking indefinitely.

## Daemon Threads

A daemon thread runs in the background and is automatically killed when all non-daemon threads have exited. This is useful for background tasks like monitoring or heartbeat threads that should not prevent the program from shutting down.

```python
import threading
import time

def background_monitor():
    while True:
        print("Monitoring...")
        time.sleep(1)

# Daemon thread: dies when main thread exits
monitor = threading.Thread(target=background_monitor, daemon=True)
monitor.start()

# Main thread does some work, then exits.
# The daemon thread is killed automatically.
time.sleep(3)
print("Main thread done. Daemon thread will be killed.")
```

Setting `daemon=True` before `start()` marks the thread as a daemon. Never use daemon threads for work that must complete (like writing to a file or committing a transaction) because the thread can be killed mid-operation without cleanup.

## ThreadPoolExecutor

For managing a pool of worker threads, `concurrent.futures.ThreadPoolExecutor` provides a higher-level API that handles thread creation, reuse, and cleanup. It is the recommended approach for most threading use cases because it avoids the boilerplate of manually creating and joining threads.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

def fetch_url(url):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return url, resp.status

urls = [
    "https://example.com",
    "https://httpbin.org/get",
    "https://jsonplaceholder.typicode.com/posts/1",
]

# submit() returns a Future object for each task
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_url, url): url for url in urls}
    for future in as_completed(futures):
        try:
            url, status = future.result()
            print(f"{url}: {status}")
        except Exception as exc:
            print(f"{futures[future]} generated an exception: {exc}")
```

The `max_workers` parameter controls the thread pool size. For I/O-bound work, a good starting point is `min(32, os.cpu_count() + 4)`, which is also the default in Python 3.8+. For CPU-bound work, threading provides no benefit regardless of pool size due to the GIL.

## executor.map for Simple Cases

When every task has the same function and you want results in submission order, `executor.map()` is cleaner than `submit()` with `as_completed()`.

```python
from concurrent.futures import ThreadPoolExecutor

def process_item(item):
    return item ** 2

items = range(20)

with ThreadPoolExecutor(max_workers=4) as executor:
    # Results are returned in the same order as the input
    results = list(executor.map(process_item, items))

print(results)  # [0, 1, 4, 9, 16, ...]
```

The tradeoff is that `map()` returns results in input order, so a slow early task blocks access to results from faster later tasks. Use `submit()` with `as_completed()` when you need results as soon as each finishes.

## Thread-Local Data

When each thread needs its own copy of some data (like a database connection), use `threading.local()`. Attributes set on a `local` object are unique to each thread.

```python
import threading

thread_data = threading.local()

def worker(name):
    thread_data.name = name  # Each thread gets its own 'name'
    process()

def process():
    # Access thread-local data without passing it as an argument
    print(f"Processing in thread: {thread_data.name}")

threads = [
    threading.Thread(target=worker, args=(f"worker-{i}",))
    for i in range(3)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

Thread-local storage is particularly useful for objects that are not thread-safe (like database cursors) or for avoiding parameter-passing through deep call chains.

## Exception Handling in Threads

Exceptions in threads do not propagate to the main thread. If a thread raises an exception and you do not catch it, the thread dies silently. With `ThreadPoolExecutor`, exceptions are captured in the `Future` object and re-raised when you call `future.result()`.

```python
from concurrent.futures import ThreadPoolExecutor

def risky_task(n):
    if n == 3:
        raise ValueError(f"Bad value: {n}")
    return n * 10

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(risky_task, i) for i in range(5)]
    for f in futures:
        try:
            print(f.result())
        except ValueError as e:
            print(f"Caught: {e}")
```

For bare `threading.Thread`, wrap the target function in a try/except and store or log the exception manually. Unhandled exceptions in threads are reported to `sys.excepthook` but do not crash the main program.

## Thread Naming for Debugging

Naming threads makes log output and debugger sessions much easier to follow. Both `Thread` and `ThreadPoolExecutor` support naming.

```python
import threading
import logging

logging.basicConfig(
    format="%(asctime)s [%(threadName)s] %(message)s",
    level=logging.INFO,
)

def task():
    logging.info("Running task")

# Named thread
t = threading.Thread(target=task, name="DataLoader")
t.start()
t.join()

# ThreadPoolExecutor uses a prefix for thread names
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2, thread_name_prefix="Fetcher") as ex:
    ex.submit(task)  # Logs as "Fetcher_0"
```

The `thread_name_prefix` parameter on `ThreadPoolExecutor` causes worker threads to be named `{prefix}_{index}`, which helps distinguish pools when multiple executors are active.

## Returning Results Without Futures

When using bare `threading.Thread`, there is no built-in mechanism to return a value. A common pattern is to use a shared mutable container or a `queue.Queue`.

```python
import threading
import queue

def compute(n, result_queue):
    result_queue.put(n * n)

q = queue.Queue()
threads = []
for i in range(5):
    t = threading.Thread(target=compute, args=(i, q))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

results = []
while not q.empty():
    results.append(q.get())

print(sorted(results))  # [0, 1, 4, 9, 16]
```

Using `queue.Queue` is thread-safe and avoids the need for manual locking. For most new code, prefer `ThreadPoolExecutor` which returns `Future` objects with a cleaner API for result retrieval.
