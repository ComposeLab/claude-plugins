# Error Handling

## Exceptions

All mq exceptions inherit from `MQError`:

```python
from mq import MQError, ConfigError, PublishError, ConsumeError, MQConnectionError, StreamError
```

| Exception | When It Happens |
|-----------|----------------|
| `ConfigError` | Config file not found, invalid YAML, missing broker references |
| `MQConnectionError` | Cannot connect to Redis or RabbitMQ |
| `PublishError` | Publish or send failed |
| `ConsumeError` | Message consumption or handler processing failed |
| `StreamError` | Stream does not exist or consumer group issue |
| `RetryExhaustedError` | All retry attempts exhausted (stream consumers) |
| `DLQError` | Failed to write to dead-letter queue |

Catch specific exceptions rather than the base `MQError`:

```python
from mq import PublishError, MQConnectionError

try:
    await bus.publish(msg)
except MQConnectionError:
    # Broker unreachable
    pass
except PublishError:
    # Message could not be published
    pass
```

## Automatic Retry (Streams Only)

Stream handlers that raise exceptions are retried automatically when `retry` is configured in YAML:

```yaml
stream:
  retry:
    max_attempts: 3   # total attempts before giving up
    base_delay: 1.0   # initial delay in seconds
  dlq: order.dlq      # dead-letter queue stream name
```

Retries use exponential backoff: delay doubles each attempt (1s → 2s → 4s). After `max_attempts`, the message routes to the DLQ stream if configured. If no DLQ is configured, the message is acknowledged and lost.

Do not catch and swallow errors inside stream handlers — let them propagate so the retry mechanism works:

```python
@Bus.stream_handler("orders", "order.created")
async def handle_order(msg: Message):
    # If this raises, the message is retried automatically
    await process_order(msg.payload)
```
