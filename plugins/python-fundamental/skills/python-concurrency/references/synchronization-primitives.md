# Synchronization Primitives

## Why Synchronization Matters

When multiple threads or processes access shared state concurrently, the order of operations is non-deterministic. Without synchronization, two threads incrementing a counter can both read the same value, both add one, and both write back — resulting in one increment instead of two. These race conditions are subtle, intermittent, and notoriously hard to reproduce. Synchronization primitives provide the tools to coordinate access and ensure correctness.

## threading.Lock

A `Lock` is the most basic synchronization primitive. Only one thread can hold the lock at a time. Other threads that try to acquire it block until it is released. Always use locks as context managers to guarantee release, even if an exception occurs.

```python
import threading

class SafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._value += 1

    @property
    def value(self):
        with self._lock:
            return self._value

counter = SafeCounter()

def worker():
    for _ in range(100_000):
        counter.increment()

threads = [threading.Thread(target=worker) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter.value)  # Always 400000
```

Without the lock, the final count would be unpredictable and almost always less than 400000.

## threading.RLock (Reentrant Lock)

An `RLock` can be acquired multiple times by the same thread without deadlocking. This is useful when a locked method calls another locked method on the same object. The lock is only released when `release()` is called as many times as `acquire()`.

```python
import threading

class SafeList:
    def __init__(self):
        self._items = []
        self._lock = threading.RLock()

    def append(self, item):
        with self._lock:
            self._items.append(item)

    def extend(self, items):
        with self._lock:
            for item in items:
                self.append(item)  # Calls append, which also acquires the lock.
                                   # RLock allows re-entry; a plain Lock would deadlock.

    def snapshot(self):
        with self._lock:
            return list(self._items)
```

Use `RLock` when you need recursive locking. For simple cases, prefer `Lock` because it is slightly faster and makes the locking protocol easier to reason about.

## Deadlock Prevention

Deadlocks occur when two or more threads each hold a lock and wait for a lock held by the other. The classic prevention strategy is to always acquire locks in a consistent global order.

```python
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()

# BAD: Thread 1 acquires A then B; Thread 2 acquires B then A → deadlock risk.
# GOOD: Both threads acquire A first, then B.

def safe_transfer():
    with lock_a:
        with lock_b:
            pass  # Both locks held safely

# For dynamic lock ordering, use the id of the lock objects:
def ordered_lock(lock1, lock2):
    first, second = sorted([lock1, lock2], key=id)
    with first:
        with second:
            pass  # Safe regardless of argument order
```

Other deadlock prevention strategies include using `lock.acquire(timeout=5)` to fail gracefully instead of blocking forever, and minimizing the scope and duration of lock-held sections.

## threading.Event

An `Event` is a simple signaling mechanism. One thread sets the event, and other threads wait for it. This is useful for one-time notifications like "initialization complete" or "shutdown requested."

```python
import threading
import time

ready_event = threading.Event()

def server():
    print("Server starting...")
    time.sleep(1)  # Simulate startup
    print("Server ready.")
    ready_event.set()  # Signal that server is ready

def client():
    print("Client waiting for server...")
    ready_event.wait()  # Blocks until the event is set
    print("Client proceeding.")

threading.Thread(target=server).start()
threading.Thread(target=client).start()
```

Events can be cleared with `event.clear()` to make them reusable, but for complex signaling patterns, consider using `Condition` instead.

## threading.Semaphore

A `Semaphore` limits the number of threads that can access a resource concurrently. This is useful for rate-limiting or capping connections to a resource.

```python
import threading
import time

# Allow at most 3 concurrent downloads
download_semaphore = threading.Semaphore(3)

def download(url):
    with download_semaphore:
        print(f"Downloading {url}")
        time.sleep(1)  # Simulate download
        print(f"Finished {url}")

threads = [
    threading.Thread(target=download, args=(f"file_{i}.dat",))
    for i in range(10)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
# At most 3 downloads run simultaneously.
```

`BoundedSemaphore` is a variant that raises an error if `release()` is called more times than `acquire()`, which helps catch programming errors.

## threading.Barrier

A `Barrier` synchronizes a fixed number of threads at a rendezvous point. All threads must reach the barrier before any can proceed. This is useful for phased computations where all workers must finish step N before any starts step N+1.

```python
import threading

barrier = threading.Barrier(4)

def phased_worker(worker_id):
    print(f"Worker {worker_id}: phase 1 complete")
    barrier.wait()  # All 4 must reach here before any proceeds
    print(f"Worker {worker_id}: starting phase 2")

threads = [
    threading.Thread(target=phased_worker, args=(i,))
    for i in range(4)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## queue.Queue (Thread-Safe)

`queue.Queue` is the standard way to pass data between threads safely. It handles all internal locking. The producer-consumer pattern is the most common use case.

```python
import threading
import queue
import time

def producer(q, items):
    for item in items:
        q.put(item)
        time.sleep(0.1)
    q.put(None)  # Sentinel value

def consumer(q, name):
    while True:
        item = q.get()
        if item is None:
            q.put(None)  # Re-post sentinel for other consumers
            break
        print(f"{name} processed: {item}")
        q.task_done()

work_queue = queue.Queue(maxsize=10)  # Bounded queue: put() blocks when full

prod = threading.Thread(target=producer, args=(work_queue, range(20)))
consumers = [
    threading.Thread(target=consumer, args=(work_queue, f"Consumer-{i}"))
    for i in range(3)
]

prod.start()
for c in consumers:
    c.start()
prod.join()
for c in consumers:
    c.join()
```

Setting `maxsize` creates backpressure: producers block when the queue is full, preventing memory from growing unbounded. `q.task_done()` and `q.join()` provide additional coordination — `q.join()` blocks until every item that has been `put()` into the queue has been matched by a `task_done()` call.

## Multiprocessing Equivalents

The `multiprocessing` module provides its own versions of these primitives that work across process boundaries.

```python
import multiprocessing

# These work across processes, not just threads:
lock = multiprocessing.Lock()
event = multiprocessing.Event()
semaphore = multiprocessing.Semaphore(3)
barrier = multiprocessing.Barrier(4)
q = multiprocessing.Queue()

# Usage is identical to threading versions:
def worker(lock, shared_value):
    with lock:
        shared_value.value += 1
```

The multiprocessing versions use OS-level synchronization (like POSIX semaphores) rather than Python-level locks, which makes them usable across processes but with higher overhead than their threading counterparts.

## concurrent.futures for Result Coordination

When you need to coordinate results from multiple parallel tasks rather than synchronize shared state, `concurrent.futures` provides a cleaner abstraction than manual locking.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED

def fetch_data(source):
    import time, random
    time.sleep(random.uniform(0.1, 1.0))
    return f"Data from {source}"

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(fetch_data, src): src
        for src in ["db", "cache", "api", "file", "backup"]
    }

    # Process results as they complete (fastest first)
    for future in as_completed(futures):
        source = futures[future]
        print(f"{source}: {future.result()}")

    # Or wait for the first result and cancel the rest:
    futures_list = [executor.submit(fetch_data, src) for src in ["primary", "fallback"]]
    done, pending = wait(futures_list, return_when=FIRST_COMPLETED)
    winner = done.pop().result()
    for f in pending:
        f.cancel()
```

The `as_completed()` function yields futures in completion order, which is ideal for aggregating results as fast as possible. The `wait()` function with `FIRST_COMPLETED` enables racing pattern where you take the first successful result and discard the rest.
