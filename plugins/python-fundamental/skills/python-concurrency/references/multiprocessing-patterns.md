# Multiprocessing Patterns

## Why Multiprocessing

Each Python process has its own interpreter and its own GIL. This means multiple processes can execute Python bytecode truly in parallel across CPU cores. The tradeoff is higher overhead: process creation is slower than thread creation, and sharing data between processes requires explicit serialization (pickling) or shared memory.

## multiprocessing.Process Basics

The `Process` class mirrors the `threading.Thread` API but spawns an OS-level process instead of a thread.

```python
import multiprocessing
import os

def worker(name):
    print(f"{name} running in PID {os.getpid()}")

if __name__ == "__main__":
    processes = []
    for i in range(4):
        p = multiprocessing.Process(target=worker, args=(f"Worker-{i}",))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    print(f"All done. Main PID: {os.getpid()}")
```

The `if __name__ == "__main__"` guard is required on Windows and macOS (with the `spawn` start method) to prevent infinite process spawning. When a new process is created via `spawn`, Python imports the main module in the child process. Without the guard, the module-level code that creates processes would run again in each child, creating more children, ad infinitum.

## ProcessPoolExecutor

The `concurrent.futures.ProcessPoolExecutor` provides the same high-level API as `ThreadPoolExecutor`, making it easy to switch between thread-based and process-based parallelism.

```python
from concurrent.futures import ProcessPoolExecutor
import math

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    numbers = range(100_000, 101_000)

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(is_prime, numbers))

    primes = [n for n, prime in zip(numbers, results) if prime]
    print(f"Found {len(primes)} primes")
```

`ProcessPoolExecutor` defaults to `os.cpu_count()` workers. For CPU-bound work, this is usually optimal. Setting `max_workers` higher than the core count wastes resources on context switching. Setting it lower leaves cores idle.

## multiprocessing.Pool

The `Pool` class predates `concurrent.futures` and offers additional methods like `starmap` and `imap` that `ProcessPoolExecutor` does not directly provide.

```python
import multiprocessing

def pow_two(x):
    return x ** 2

def multiply(x, y):
    return x * y

if __name__ == "__main__":
    with multiprocessing.Pool(processes=4) as pool:
        # map: single-argument function
        squares = pool.map(pow_two, range(10))

        # starmap: multi-argument function
        pairs = [(2, 3), (4, 5), (6, 7)]
        products = pool.starmap(multiply, pairs)
        print(products)  # [6, 20, 42]

        # imap: lazy iterator, useful for large datasets
        for result in pool.imap(pow_two, range(1000), chunksize=100):
            pass  # Process results one at a time
```

The `chunksize` parameter in `map`, `starmap`, and `imap` controls how many items are sent to each worker at once. Larger chunks reduce IPC overhead but decrease granularity. For many small tasks, a larger chunksize (e.g., 100-1000) can dramatically improve throughput.

## Sharing State Between Processes

Processes do not share memory by default. There are several mechanisms for sharing state, each with different tradeoffs.

### Value and Array

`multiprocessing.Value` and `multiprocessing.Array` use shared memory with built-in locking.

```python
import multiprocessing

def increment(counter, lock):
    for _ in range(10_000):
        with lock:
            counter.value += 1

if __name__ == "__main__":
    counter = multiprocessing.Value("i", 0)  # 'i' = signed int
    lock = multiprocessing.Lock()

    processes = [
        multiprocessing.Process(target=increment, args=(counter, lock))
        for _ in range(4)
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    print(f"Counter: {counter.value}")  # 40000
```

### Manager

A `Manager` creates a server process that holds Python objects and provides proxy access from other processes. This supports complex types (lists, dicts, Namespaces) but is slower than `Value`/`Array` because every access involves IPC.

```python
import multiprocessing

def add_items(shared_list, items):
    for item in items:
        shared_list.append(item)

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        shared = manager.list()
        p1 = multiprocessing.Process(target=add_items, args=(shared, [1, 2, 3]))
        p2 = multiprocessing.Process(target=add_items, args=(shared, [4, 5, 6]))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        print(sorted(shared))  # [1, 2, 3, 4, 5, 6]
```

### SharedMemory (Python 3.8+)

For high-performance sharing of large data buffers, `multiprocessing.shared_memory.SharedMemory` provides raw shared memory without the overhead of a manager process.

```python
from multiprocessing import shared_memory, Process
import numpy as np

def fill_array(shm_name, shape, dtype):
    existing = shared_memory.SharedMemory(name=shm_name)
    arr = np.ndarray(shape, dtype=dtype, buffer=existing.buf)
    arr[:] = arr * 2  # Modify in place
    existing.close()

if __name__ == "__main__":
    data = np.array([1, 2, 3, 4, 5], dtype=np.float64)
    shm = shared_memory.SharedMemory(create=True, size=data.nbytes)
    shared_arr = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
    shared_arr[:] = data

    p = Process(target=fill_array, args=(shm.name, data.shape, data.dtype))
    p.start()
    p.join()

    print(shared_arr)  # [2. 4. 6. 8. 10.]
    shm.close()
    shm.unlink()
```

## Pipe and Queue for IPC

`Pipe` creates a bidirectional connection between two processes. `Queue` provides a multi-producer, multi-consumer FIFO queue.

```python
import multiprocessing

def producer(q, items):
    for item in items:
        q.put(item)
    q.put(None)  # Sentinel to signal completion

def consumer(q):
    results = []
    while True:
        item = q.get()
        if item is None:
            break
        results.append(item * 2)
    print(f"Processed: {results}")

if __name__ == "__main__":
    q = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=producer, args=(q, [1, 2, 3, 4]))
    p2 = multiprocessing.Process(target=consumer, args=(q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

Use `Queue` when multiple producers or consumers are involved. Use `Pipe` for simple two-process communication where the lower overhead matters.

## Start Methods

Python supports three process start methods, configured via `multiprocessing.set_start_method()` or `multiprocessing.get_context()`.

**fork** (default on Linux): Copies the parent process via `os.fork()`. Fast, but can cause issues with threads or locks held at fork time. Not safe if the parent has multiple threads.

**spawn** (default on macOS/Windows): Starts a fresh Python interpreter. Safer than fork because there is no inherited state, but slower because the module must be imported from scratch. Requires all arguments to be picklable.

**forkserver**: A hybrid that forks from a clean server process. Safer than fork, faster than spawn for repeated process creation.

```python
import multiprocessing

# Set once at program start, before any Process is created.
if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")

    # Or use a context for isolated configuration:
    ctx = multiprocessing.get_context("forkserver")
    p = ctx.Process(target=some_function)
```

For new code, `spawn` is the safest default. Use `fork` only when you understand the implications and need the performance. Use `forkserver` as a middle ground in long-running applications that create many processes.
