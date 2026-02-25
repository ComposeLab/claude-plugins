# Configuration

The mq library uses a single YAML file for all messaging config. Set the `MQ_CONFIG_PATH` environment variable to point to it:

```bash
export MQ_CONFIG_PATH=mq.yaml
```

## Example Config

```yaml
brokers:
  redis-main:
    type: redis
    host: localhost
    port: 6379
    db: 0

buses:
  # Pub/sub bus — fire-and-forget notifications
  events:
    broker: redis-main
    pubsub:
      topics:
        - "order.*"
        - "payment.*"

  # Stream bus — guaranteed delivery with consumer groups
  orders:
    broker: redis-main
    stream:
      streams:
        - order.created
        - order.updated
      consumer_group: order-service
      consumer_name: worker-1
      prefetch: 10
      retry:
        max_attempts: 3
        base_delay: 1.0
      dlq: order.dlq

  # Delayed messaging bus
  scheduler:
    broker: redis-main
    delayed: true
    stream:
      streams:
        - scheduled.tasks
```

## Brokers

Three broker types. Swap the `broker` field on any bus — zero code changes.

| Type | Use Case |
|------|----------|
| `redis` | Production. Supports pub/sub, streams, delayed, caching. |
| `rabbitmq` | Production. Supports pub/sub, streams, delayed. |
| `memory` | Testing only. Supports pub/sub and streams. No persistence. |

Redis config: `type`, `host`, `port`, `db`.
RabbitMQ config: `type`, `host`, `port`, `username`, `password`, `virtual_host`.
Memory config: just `type: memory`.

## Buses

Each bus needs a `broker` reference and at least one capability:

**pubsub** — Topic patterns to subscribe to.

**stream** — Stream names to consume from, plus:
- `consumer_group` — Group name (default: `"default"`)
- `consumer_name` — This worker's identity (default: `"worker-1"`)
- `prefetch` — Max unacknowledged messages per read (default: `10`)
- `retry` — Automatic retry with exponential backoff: `max_attempts`, `base_delay`
- `dlq` — Dead-letter queue stream name for messages that exhaust retries

**delayed** — Set to `true` for defaults. Delayed messages are delivered to the stream configured on the same bus.

## Scaling Consumers

Deploy multiple instances with the same `consumer_group` but different `consumer_name`. The broker distributes messages across the group.

```yaml
# Instance 1: consumer_name: worker-1
# Instance 2: consumer_name: worker-2
```

## Testing Config

Use the `memory` broker for tests — no external services needed:

```yaml
brokers:
  test:
    type: memory
buses:
  events:
    broker: test
    pubsub:
      topics: ["order.*"]
  orders:
    broker: test
    stream:
      streams: [order.created]
      consumer_group: test-group
      consumer_name: test-worker
```
