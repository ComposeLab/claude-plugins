---
name: core-mq
description: Guides writing async messaging code and configuring projects using the mq unified message queue library.
version: 1.0.0
author: composeLab
triggers:
  - "use mq"
  - "set up message queue"
  - "publish a message"
  - "create a stream consumer"
  - "add delayed messaging"
tags:
  - messaging
  - python
  - internal
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: true
---

# core-mq

Assists with writing async messaging code using the mq library. The library provides pub/sub, streams, and delayed messaging across Redis, RabbitMQ, and in-memory brokers through a single YAML config — swap brokers with zero code changes.

## Workflow: Write Messaging Code

### Step 1: Understand the Task

Identify the messaging pattern needed: pub/sub (fire-and-forget notifications), streams (guaranteed delivery with consumer groups), or delayed messaging (scheduled tasks). Clarify message types and delivery guarantees if ambiguous.

### Step 2: Write the Code

Consult [API Reference](references/api-reference.md) for Bus methods and Message creation. All code uses one import: `from mq import Bus, Message, setup_bus_factory`.

For pub/sub, use `Bus.publish()` to send and `@Bus.subscriber()` to receive. Messages published while no subscriber is connected are lost.

For streams, use `Bus.send()` to append and `@Bus.stream_handler()` to consume. Each message in a consumer group goes to exactly one consumer. If the handler raises, the message is retried automatically.

For delayed messaging, use `Bus.publish_delayed()` for relative delays or `Bus.publish_at()` for absolute UTC times. Delayed messages are consumed as streams.

Consult [Common Patterns](references/patterns.md) for complete examples of each pattern.

### Step 3: Handle Errors

Consult [Error Handling](references/error-handling.md) for exceptions and retry/DLQ behavior. For stream consumers, configure `retry` and `dlq` in YAML — the library handles retries automatically.

### Step 4: Review

Verify handlers are registered before `start()`, all handlers are `async def`, and buses are closed on shutdown.

## Workflow: Configure mq

### Step 1: Determine the Broker

Identify whether the project uses Redis, RabbitMQ, or the in-memory broker. Redis is the most common choice; in-memory is for testing only.

### Step 2: Set Up Configuration

Consult [Configuration](references/configuration.md) for the YAML format. Create `mq.yaml` with brokers and buses. Set the `MQ_CONFIG_PATH` environment variable to point to the config file.

### Step 3: Verify

Confirm each bus references an existing broker and has at least one capability (pubsub, stream, or delayed).
