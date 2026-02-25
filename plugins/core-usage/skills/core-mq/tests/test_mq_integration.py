"""Integration tests for core-mq skill.

Tests the real user experience: YAML config → import → use.
Uses the in-memory broker — no external services required.
"""

import pytest
import yaml
from pathlib import Path

from mq import Bus, Message, setup_bus_factory


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_bus():
    """Clean Bus state between tests."""
    Bus._registry.clear()
    Bus._factory = None
    Bus._pending_handlers.clear()
    yield
    Bus._registry.clear()
    Bus._factory = None
    Bus._pending_handlers.clear()


@pytest.fixture
def config_file(tmp_path):
    """Write a test mq.yaml and return its path."""
    config = {
        "brokers": {
            "test": {"type": "memory"},
        },
        "buses": {
            "events": {
                "broker": "test",
                "pubsub": {"topics": ["order.*", "payment.*"]},
            },
            "orders": {
                "broker": "test",
                "stream": {
                    "streams": ["order.created", "order.updated"],
                    "consumer_group": "test-group",
                    "consumer_name": "test-worker",
                },
            },
        },
    }
    path = tmp_path / "mq.yaml"
    path.write_text(yaml.dump(config))
    return path


def setup_from_file(config_file: Path):
    """Load config from YAML file, same as a real user would."""
    from mq.config.loader import load_config
    cfg = load_config(str(config_file), use_cache=False)
    setup_bus_factory(cfg)


# ---------------------------------------------------------------------------
# Test: The core workflow — config → setup → get → start → use → close
# ---------------------------------------------------------------------------

class TestCoreWorkflow:
    async def test_pubsub_publish_and_receive(self, config_file):
        """User publishes a message, subscriber receives it."""
        setup_from_file(config_file)

        received = []

        @Bus.subscriber("events", "order.*")
        async def handle_order(msg: Message):
            received.append(msg)

        bus = await Bus.get("events")
        await bus.start()

        await bus.publish(Message(type="order.created", payload={"order_id": 1}))

        assert len(received) == 1
        assert received[0].type == "order.created"
        assert received[0].payload == {"order_id": 1}

        await bus.close()

    async def test_stream_send_and_consume(self, config_file):
        """User sends to a stream, consumer receives with guaranteed delivery."""
        setup_from_file(config_file)

        received = []

        @Bus.stream_handler("orders", "order.created")
        async def handle_order(msg: Message):
            received.append(msg)

        bus = await Bus.get("orders")
        await bus.start()

        entry_id = await bus.send(
            Message(type="order.created", payload={"order_id": 42})
        )

        assert entry_id is not None
        assert len(received) == 1
        assert received[0].payload == {"order_id": 42}

        await bus.close()

    async def test_multiple_buses(self, config_file):
        """User runs multiple buses with start_all/close_all."""
        setup_from_file(config_file)

        pubsub_msgs = []
        stream_msgs = []

        @Bus.subscriber("events", "order.*")
        async def on_event(msg: Message):
            pubsub_msgs.append(msg)

        @Bus.stream_handler("orders", "order.created")
        async def on_order(msg: Message):
            stream_msgs.append(msg)

        events = await Bus.get("events")
        orders = await Bus.get("orders")
        await Bus.start_all()

        await events.publish(Message(type="order.created", payload={"via": "pubsub"}))
        await orders.send(Message(type="order.created", payload={"via": "stream"}))

        assert len(pubsub_msgs) == 1
        assert pubsub_msgs[0].payload == {"via": "pubsub"}
        assert len(stream_msgs) == 1
        assert stream_msgs[0].payload == {"via": "stream"}

        await Bus.close_all()


# ---------------------------------------------------------------------------
# Test: Message creation and serialization
# ---------------------------------------------------------------------------

class TestMessage:
    def test_create_with_type_only(self):
        """Minimal message — only type is required."""
        msg = Message(type="order.created")
        assert msg.type == "order.created"
        assert msg.payload == {}
        assert msg.id  # auto UUID
        assert msg.timestamp  # auto UTC

    def test_create_with_payload_and_headers(self):
        msg = Message(
            type="order.created",
            payload={"id": 1, "total": 50},
            headers={"x-source": "api"},
        )
        assert msg.payload["total"] == 50
        assert msg.headers["x-source"] == "api"

    def test_roundtrip_dict(self):
        original = Message(type="test", payload={"key": "value"})
        restored = Message.from_dict(original.to_dict())
        assert restored.type == original.type
        assert restored.payload == original.payload
        assert restored.id == original.id

    def test_roundtrip_json(self):
        original = Message(type="test", payload={"key": "value"})
        restored = Message.from_json(original.to_json())
        assert restored.type == original.type
        assert restored.payload == original.payload


# ---------------------------------------------------------------------------
# Test: Pattern matching
# ---------------------------------------------------------------------------

class TestPatternMatching:
    async def test_wildcard_matches_subtypes(self, config_file):
        """order.* matches order.created and order.updated."""
        setup_from_file(config_file)

        received = []

        async def handler(msg: Message):
            received.append(msg)

        bus = await Bus.get("events")
        bus.on("order.*", handler)
        await bus.start()

        await bus.publish(Message(type="order.created"))
        await bus.publish(Message(type="order.updated"))
        await bus.publish(Message(type="payment.received"))  # should NOT match

        assert len(received) == 2
        await bus.close()


# ---------------------------------------------------------------------------
# Test: Handler registration
# ---------------------------------------------------------------------------

class TestHandlerRegistration:
    async def test_on_before_start(self, config_file):
        """Handlers registered with bus.on() before start() work."""
        setup_from_file(config_file)

        received = []

        async def handler(msg: Message):
            received.append(msg)

        bus = await Bus.get("events")
        bus.on("order.*", handler)
        await bus.start()

        await bus.publish(Message(type="order.created"))
        assert len(received) == 1
        await bus.close()

    async def test_decorator_registration(self, config_file):
        """@Bus.subscriber decorator registers at import time."""
        setup_from_file(config_file)

        received = []

        @Bus.subscriber("events", "payment.*")
        async def handle(msg: Message):
            received.append(msg)

        bus = await Bus.get("events")
        await bus.start()

        await bus.publish(Message(type="payment.received", payload={"amount": 100}))
        assert len(received) == 1
        assert received[0].payload == {"amount": 100}
        await bus.close()


# ---------------------------------------------------------------------------
# Test: Bus lifecycle
# ---------------------------------------------------------------------------

class TestLifecycle:
    async def test_get_returns_same_bus(self, config_file):
        """Bus.get() caches — calling twice returns the same instance."""
        setup_from_file(config_file)
        bus1 = await Bus.get("events")
        bus2 = await Bus.get("events")
        assert bus1 is bus2

    async def test_get_without_setup_raises(self):
        """Bus.get() without setup_bus_factory() raises RuntimeError."""
        with pytest.raises(RuntimeError):
            await Bus.get("events")

    async def test_resolve_after_get(self, config_file):
        """Bus.resolve() returns a previously created bus synchronously."""
        setup_from_file(config_file)
        bus = await Bus.get("events")
        assert Bus.resolve("events") is bus

    async def test_resolve_unknown_raises(self):
        """Bus.resolve() raises KeyError for unknown bus."""
        with pytest.raises(KeyError):
            Bus.resolve("nonexistent")


# ---------------------------------------------------------------------------
# Test: YAML config loading
# ---------------------------------------------------------------------------

class TestConfig:
    def test_load_from_yaml(self, config_file):
        """Config loads from a YAML file."""
        from mq.config.loader import load_config
        cfg = load_config(str(config_file), use_cache=False)
        assert "test" in cfg.brokers
        assert "events" in cfg.buses
        assert "orders" in cfg.buses

    def test_load_from_env(self, config_file, monkeypatch):
        """Config loads from MQ_CONFIG_PATH environment variable."""
        from mq.config.loader import load_config
        monkeypatch.setenv("MQ_CONFIG_PATH", str(config_file))
        cfg = load_config(use_cache=False)
        assert "events" in cfg.buses

    def test_bus_requires_capability(self):
        """A bus with no pubsub/stream/delayed is rejected."""
        from mq.config.models import BrokerConfig, BusConfig, MQConfig
        with pytest.raises(Exception):
            MQConfig(
                brokers={"mem": BrokerConfig(type="memory")},
                buses={"empty": BusConfig(broker="mem")},
            )

    def test_invalid_broker_reference_rejected(self):
        """A bus referencing a nonexistent broker is rejected."""
        from mq.config.models import BrokerConfig, BusConfig, MQConfig, PubSubConfig
        with pytest.raises(Exception):
            MQConfig(
                brokers={"mem": BrokerConfig(type="memory")},
                buses={"bad": BusConfig(broker="nonexistent", pubsub=PubSubConfig())},
            )
