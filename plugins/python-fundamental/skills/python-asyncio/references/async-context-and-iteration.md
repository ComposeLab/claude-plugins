# Async Context and Iteration

## Async Context Managers

Async context managers follow the same protocol as regular context managers but use coroutine methods: `__aenter__` and `__aexit__`. They are entered with `async with` instead of `with`. This allows the setup and teardown phases to perform asynchronous operations like opening network connections or acquiring distributed locks.

```python
import asyncio

class AsyncDatabaseConnection:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None

    async def __aenter__(self):
        print(f"Connecting to {self.dsn}")
        await asyncio.sleep(0.1)  # simulate async connect
        self.conn = {"status": "connected"}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        await asyncio.sleep(0.05)  # simulate async close
        self.conn = None
        return False  # Do not suppress exceptions.

async def main():
    async with AsyncDatabaseConnection("postgres://localhost/db") as db:
        print(f"Connection status: {db.conn['status']}")
    # Connection is guaranteed closed here, even if an exception occurred.

asyncio.run(main())
```

The `return False` in `__aexit__` means exceptions propagate normally. Returning `True` would suppress the exception, which is rarely what you want.

## @asynccontextmanager Decorator

Writing a full class for every async context manager is verbose. The `contextlib.asynccontextmanager` decorator lets you write one using a single async generator function. Everything before `yield` is the setup (`__aenter__`), and everything after is the teardown (`__aexit__`).

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_connection(dsn: str):
    print(f"Connecting to {dsn}")
    conn = await create_connection(dsn)
    try:
        yield conn
    finally:
        print("Closing connection")
        await conn.close()

async def main():
    async with managed_connection("postgres://localhost/db") as conn:
        await conn.execute("SELECT 1")
```

The `try/finally` around `yield` ensures cleanup runs even if the body of the `async with` block raises an exception. Omitting `finally` means cleanup is skipped on errors, leading to resource leaks.

## Async For Loops

`async for` iterates over an async iterable, an object that implements `__aiter__` and `__anext__` as coroutines. Each iteration can perform asynchronous work to produce the next value, making it natural for streaming data from network sources, databases, or message queues.

```python
import asyncio

class AsyncCounter:
    def __init__(self, limit: int):
        self.limit = limit
        self.current = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.limit:
            raise StopAsyncIteration
        self.current += 1
        await asyncio.sleep(0.1)  # simulate async data fetch
        return self.current

async def main():
    async for number in AsyncCounter(5):
        print(number)

asyncio.run(main())
```

`async for` suspends at each iteration while waiting for the next value, allowing other coroutines to run between items. This makes it ideal for processing streams where items arrive over time.

## Async Generators

Async generators combine `async def` with `yield` to create async iterables without writing a full class. They are the async equivalent of regular generator functions and are the most concise way to produce async streams.

```python
import asyncio

async def fetch_pages(base_url: str, total_pages: int):
    """Async generator that yields page data one at a time."""
    for page in range(1, total_pages + 1):
        await asyncio.sleep(0.2)  # simulate HTTP request
        yield {"page": page, "data": f"Content of page {page}"}

async def main():
    async for page in fetch_pages("https://api.example.com", 5):
        print(f"Processing page {page['page']}")

asyncio.run(main())
```

Async generators support `async for` iteration and can also be manually advanced with `await gen.__anext__()` or `await gen.asend(value)`. They are cleaned up automatically when the event loop shuts down, but you can also close them explicitly with `await gen.aclose()`.

## aiohttp Session as Async Context Manager

The `aiohttp` library is the most common HTTP client for asyncio. Its `ClientSession` is designed as an async context manager that manages a connection pool. Creating one session and reusing it across requests is far more efficient than creating a new session per request.

```python
import aiohttp
import asyncio

async def fetch_urls(urls: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        results = []
        for url in urls:
            async with session.get(url) as response:
                text = await response.text()
                results.append(text)
        return results

async def main():
    urls = ["https://httpbin.org/get"] * 3
    pages = await fetch_urls(urls)
    print(f"Fetched {len(pages)} pages")

asyncio.run(main())
```

The outer `async with` manages the session lifecycle (connection pool creation and teardown). The inner `async with session.get(url)` manages the individual response (reading the body and releasing the connection back to the pool). Both levels are important: skipping the session context manager leaks connections, and skipping the response context manager delays connection reuse.

## Async File I/O Patterns

Standard file operations (`open`, `read`, `write`) are synchronous and block the event loop. The `aiofiles` library provides async wrappers that offload file I/O to a thread pool while presenting an async interface.

```python
import aiofiles
import asyncio

async def read_file(path: str) -> str:
    async with aiofiles.open(path, mode="r") as f:
        contents = await f.read()
    return contents

async def write_file(path: str, data: str):
    async with aiofiles.open(path, mode="w") as f:
        await f.write(data)

async def main():
    await write_file("output.txt", "Hello, async world!")
    content = await read_file("output.txt")
    print(content)

asyncio.run(main())
```

If `aiofiles` is not available, you can use `asyncio.to_thread()` to offload standard file operations without blocking the loop:

```python
async def read_file_stdlib(path: str) -> str:
    return await asyncio.to_thread(lambda: open(path).read())
```

## Streaming Data with Async Generators

Async generators shine when processing large data streams that should not be loaded entirely into memory. By yielding items one at a time, they enable pipeline-style processing where each stage processes and forwards items independently.

```python
import asyncio

async def read_lines(path: str):
    """Stream lines from a file without loading it all into memory."""
    async with aiofiles.open(path) as f:
        async for line in f:
            yield line.strip()

async def filter_lines(lines, keyword: str):
    """Filter an async stream of lines by keyword."""
    async for line in lines:
        if keyword in line:
            yield line

async def main():
    raw_lines = read_lines("server.log")
    error_lines = filter_lines(raw_lines, "ERROR")

    async for line in error_lines:
        print(line)

asyncio.run(main())
```

This pipeline pattern composes naturally: each async generator wraps another, building a processing chain that flows data through without buffering the entire dataset. Memory usage stays constant regardless of file size.
