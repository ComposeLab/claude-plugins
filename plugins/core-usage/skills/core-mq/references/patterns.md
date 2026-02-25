# Common Patterns

All patterns use the same import and setup:

```python
from mq import Bus, Message, setup_bus_factory
setup_bus_factory()  # loads from MQ_CONFIG_PATH
```

## Pub/Sub: Notifications

Publisher sends, subscriber listens. Messages lost if no subscriber is connected.

```python
# publisher.py
bus = await Bus.get("events")
await bus.start()
await bus.publish(Message(type="order.created", payload={"order_id": 1}))
```

```python
# subscriber.py
@Bus.subscriber("events", "order.*")
async def handle_order(msg: Message):
    print(f"Received: {msg.payload}")

await Bus.get("events")
await Bus.start_all()
```

## Streams: Guaranteed Delivery

Producer appends to stream, consumer reads with consumer group. Messages survive restarts.

```python
# producer.py
bus = await Bus.get("orders")
await bus.start()
entry_id = await bus.send(Message(type="order.created", payload={"order_id": 1}))
```

```python
# consumer.py
@Bus.stream_handler("orders", "order.created")
async def handle_order(msg: Message):
    print(f"Processing: {msg.payload}")

await Bus.get("orders")
await Bus.start_all()
```

Stop and restart the consumer — it resumes from where it left off.

## Delayed Messaging: Scheduled Tasks

Schedule messages for future delivery. Requires Redis or RabbitMQ.

```python
# publisher.py
bus = await Bus.get("scheduler")
await bus.start()
await bus.publish_delayed(
    Message(type="reminder", payload={"text": "Hello from the past!"}),
    delay_seconds=5,
)
```

```python
# consumer.py (same as stream consumer)
@Bus.stream_handler("scheduler", "scheduled.tasks")
async def handle_reminder(msg: Message):
    print(f"Received: {msg.payload}")
```

## Application Lifecycle

Typical startup and shutdown:

```python
import asyncio
from mq import Bus, Message, setup_bus_factory

# Handlers registered at import time via decorators
import app.handlers  # noqa: F401

async def main():
    setup_bus_factory()
    await Bus.start_all()
    try:
        await asyncio.Event().wait()
    finally:
        await Bus.close_all()

asyncio.run(main())
```

## Testing with In-Memory Broker

Point `MQ_CONFIG_PATH` at a test config that uses `type: memory`:

```python
import os
os.environ["MQ_CONFIG_PATH"] = "test_mq.yaml"

from mq import Bus, Message, setup_bus_factory

async def test_order_handler():
    setup_bus_factory()
    bus = await Bus.get("orders")

    received = []
    bus.on_stream("order.created", lambda msg: received.append(msg))
    await bus.start()

    await bus.send(Message(type="order.created", payload={"id": 1}))
    assert len(received) == 1

    await Bus.close_all()
```
