# GIL and Execution Model

## What the GIL Is

The Global Interpreter Lock (GIL) is a mutex in CPython that allows only one thread to execute Python bytecode at a time. Even on a machine with 16 cores, a pure-Python multithreaded program effectively runs on a single core for CPU-bound work. The GIL does not prevent threads from being created or scheduled by the OS — it prevents them from running Python instructions simultaneously.

This is a CPython implementation detail, not a Python language requirement. Other implementations like Jython and IronPython do not have a GIL. However, since CPython is the dominant implementation, the GIL shapes how most Python developers think about concurrency.

## Why the GIL Exists

CPython manages memory through reference counting. Every Python object has a reference count, and when that count drops to zero, the object is deallocated. Without the GIL, every reference count update would need its own lock, which would slow down single-threaded programs significantly and introduce the risk of deadlocks across the interpreter. The GIL is a pragmatic tradeoff: single-threaded performance stays fast, C extensions remain simple to write, and the interpreter internals stay coherent without fine-grained locking.

## How the GIL Affects Threading

When multiple threads run Python code, the GIL forces them to take turns. CPython switches threads approximately every 5 milliseconds (configurable via `sys.setswitchinterval`). This means threads run concurrently (they interleave) but not in parallel (they do not execute simultaneously on different cores).

```python
import threading
import time

def cpu_work(n):
    """Pure Python CPU-bound work."""
    total = 0
    for i in range(n):
        total += i * i
    return total

# This will NOT be faster than sequential execution
# because the GIL prevents parallel bytecode execution.
threads = []
start = time.perf_counter()
for _ in range(4):
    t = threading.Thread(target=cpu_work, args=(10_000_000,))
    threads.append(t)
    t.start()
for t in threads:
    t.join()
elapsed_threaded = time.perf_counter() - start

start = time.perf_counter()
for _ in range(4):
    cpu_work(10_000_000)
elapsed_sequential = time.perf_counter() - start

print(f"Threaded: {elapsed_threaded:.2f}s")
print(f"Sequential: {elapsed_sequential:.2f}s")
# Threaded is often SLOWER due to lock contention and context switching.
```

## When the GIL Is Released

The GIL is released during blocking I/O operations — file reads, network calls, `time.sleep`, and similar system calls. This is why threading works well for I/O-bound tasks: while one thread waits for a network response, another thread can execute Python code.

```python
import threading
import urllib.request
import time

def fetch(url):
    """I/O-bound work: GIL is released during the network call."""
    with urllib.request.urlopen(url) as response:
        return len(response.read())

urls = ["https://example.com"] * 10

# Threaded I/O IS faster because the GIL is released during network waits.
start = time.perf_counter()
threads = []
for url in urls:
    t = threading.Thread(target=fetch, args=(url,))
    threads.append(t)
    t.start()
for t in threads:
    t.join()
print(f"Threaded I/O: {time.perf_counter() - start:.2f}s")
```

Many C extensions also release the GIL during computation. NumPy releases the GIL for array operations, which means NumPy-heavy threaded code can achieve true parallelism. The `hashlib` module and `zlib` compression also release the GIL.

## CPU-Bound vs I/O-Bound Implications

For CPU-bound work (number crunching, data transformation, image processing), threads provide no speedup and may slow things down. Use `multiprocessing` to sidestep the GIL entirely — each process has its own interpreter and its own GIL.

For I/O-bound work (network requests, file I/O, database queries), threads work well because the GIL is released during waits. `asyncio` is another option that uses a single thread with cooperative scheduling and often has lower overhead than threading for high-concurrency I/O.

## GIL-Free Python (PEP 703)

Python 3.13 introduced an experimental free-threading build that disables the GIL. This is enabled via the `--disable-gil` configure flag when building CPython, or by installing the `python3.13t` variant. The free-threaded build allows true parallel execution of Python bytecode across threads.

```python
# To check if your Python build has the GIL disabled:
import sys
if hasattr(sys, '_is_gil_enabled'):
    print(f"GIL enabled: {sys._is_gil_enabled()}")
else:
    print("GIL status API not available (Python < 3.13)")
```

The free-threading build is still experimental. Many C extensions are not yet compatible, and single-threaded performance may be slightly slower. For production use in 2025-2026, the standard GIL-enabled build remains the safe default, and `multiprocessing` remains the reliable way to achieve CPU parallelism.

## Benchmarking to Verify Parallelism

Never assume parallelism — measure it. The pattern below helps verify whether your concurrency approach actually provides a speedup.

```python
import time
import multiprocessing
import concurrent.futures

def heavy_computation(n):
    return sum(i * i for i in range(n))

N = 5_000_000
TASKS = 8

# Sequential baseline
start = time.perf_counter()
results_seq = [heavy_computation(N) for _ in range(TASKS)]
seq_time = time.perf_counter() - start

# Multiprocessing (true parallelism)
start = time.perf_counter()
with concurrent.futures.ProcessPoolExecutor() as executor:
    results_mp = list(executor.map(heavy_computation, [N] * TASKS))
mp_time = time.perf_counter() - start

print(f"Sequential:      {seq_time:.2f}s")
print(f"Multiprocessing: {mp_time:.2f}s")
print(f"Speedup:         {seq_time / mp_time:.1f}x")
```

If the speedup is close to 1x, the overhead of inter-process communication is eating the gains, or the task is too small. Increase the work per task or reduce the number of tasks to find the sweet spot.
