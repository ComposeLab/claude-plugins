# API Reference

Source: `/Users/hieu/WorkingSpace/ComposeLab/mq`.

Every example in this library uses one import:

```python
from mq import Bus, Message, setup_bus_factory
```

## setup_bus_factory

Call once at startup. Loads config from the `MQ_CONFIG_PATH` environment variable.

```python
setup_bus_factory()
```

After this, `Bus.get()` creates buses on demand from the YAML config.

## Bus

The messaging hub. Get one by name from config, start it, use it.

```python
bus = await Bus.get("events")
await bus.start()
```

### Pub/Sub

```python
# Publish
await bus.publish(Message(type="order.created", payload={"id": 1}))

# Subscribe (register before start)
bus.on("order.*", handler)

# Or use the decorator (registers at import time)
@Bus.subscriber("events", "order.*")
async def handle_order(msg: Message):
    print(msg.payload)
```

Patterns use fnmatch: `*` matches any sequence, `?` matches one char. Messages sent while no subscriber is connected are lost.

### Streams

```python
# Send to stream
entry_id = await bus.send(Message(type="order.created", payload={"id": 1}))

# Consume (register before start)
bus.on_stream("order.created", handler)

# Or use the decorator
@Bus.stream_handler("orders", "order.created")
async def handle_order(msg: Message):
    print(msg.payload)
```

Streams provide at-least-once delivery. Each message in a consumer group goes to exactly one consumer. If the handler raises, the message is retried automatically. After all retries, it routes to the DLQ (if configured).

### Delayed Messaging

```python
# Deliver after 60 seconds
await bus.publish_delayed(msg, delay_seconds=60)

# Deliver at a specific UTC time
from datetime import datetime, timezone
await bus.publish_at(msg, scheduled_time=datetime(2024, 12, 1, tzinfo=timezone.utc))
```

### Lifecycle

```python
await bus.start()          # Connect and start consumers
await bus.close()          # Stop and cleanup

await Bus.start_all()      # Start all buses in registry
await Bus.close_all()      # Close all buses
```

## Message

A simple dataclass. Only `type` is required.

```python
msg = Message(
    type="order.created",           # routing key (required)
    payload={"id": 1, "total": 50}, # arbitrary data (default: {})
    headers={"x-source": "api"},    # optional metadata (default: {})
)
```

`id` (UUID) and `timestamp` (UTC) are auto-generated.

Serialization: `msg.to_dict()`, `msg.to_json()`, `Message.from_dict(data)`, `Message.from_json(raw)`.

## Handlers

Handlers are async functions that accept a `Message`:

```python
async def my_handler(msg: Message) -> None:
    print(msg.type, msg.payload)
```

Register handlers before calling `start()`. Decorators (`@Bus.subscriber`, `@Bus.stream_handler`) register at import time — they get wired when `Bus.get()` is called.

## Typical Application

```python
import asyncio
from mq import Bus, Message, setup_bus_factory

@Bus.stream_handler("orders", "order.created")
async def handle_order(msg: Message):
    print(f"Processing order {msg.payload['id']}")

async def main():
    setup_bus_factory()
    await Bus.get("orders")
    await Bus.start_all()

    try:
        await asyncio.Event().wait()
    finally:
        await Bus.close_all()

asyncio.run(main())
```
