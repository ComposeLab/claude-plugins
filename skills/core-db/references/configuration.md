# core-db Configuration

## Environment Variable

core-db loads configuration from a directory specified by the `CONFIG_PATH` environment variable:

```bash
export CONFIG_PATH=/path/to/config/directory
```

The library looks for `db_config.yaml` inside this directory.

## Configuration File Format

`db_config.yaml` defines named database connections:

```yaml
databases:
  default: main
  connections:
    main:
      driver: postgresql
      host: localhost
      port: 5432
      database: mydb
      username: user
      password: pass
      pool_size: 10
      pool_timeout: 30
      echo: false
      view_pool_reservation: 0.1
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `driver` | string | yes | `postgresql` or `sqlite` |
| `host` | string | yes (pg) | Database host |
| `port` | int | yes (pg) | Database port (default 5432) |
| `database` | string | yes | Database name or file path |
| `username` | string | yes (pg) | Connection username |
| `password` | string | yes (pg) | Connection password |
| `pool_size` | int | no | Connection pool size (default varies) |
| `pool_timeout` | int | no | Pool timeout in seconds |
| `echo` | bool | no | Log all SQL statements (default false) |
| `view_pool_reservation` | float | no | Fraction of pool reserved for reads (0.0–0.5, default 0.1) |

### Multiple Connections

Define multiple named connections under `connections:`. Set `default:` to the connection name used when no explicit connection is specified.

```yaml
databases:
  default: primary
  connections:
    primary:
      driver: postgresql
      host: prod-db.internal
      port: 5432
      database: app_db
      username: app_user
      password: secret
      pool_size: 20
    analytics:
      driver: postgresql
      host: analytics-db.internal
      port: 5432
      database: analytics_db
      username: reader
      password: readonly
      pool_size: 5
```

### SQLite Configuration

For local development or testing:

```yaml
databases:
  default: local
  connections:
    local:
      driver: sqlite
      database: ./local.db
```

SQLite uses a static pool (no connection pooling). In-memory databases are supported with `database: ":memory:"`.

## View Pool Reservation

The `view_pool_reservation` setting controls what fraction of the connection pool is reserved for read operations (ViewManager). This prevents heavy read traffic from starving write operations.

- `0.0` — No reservation, reads and writes share the full pool
- `0.1` — 10% of connections reserved for reads (default)
- `0.5` — Maximum allowed, 50% reserved for reads

## Logging Configuration

An optional `logging.yaml` in the same config directory controls log output. If absent, defaults apply. core-db uses per-module loggers and supports debug-level logging for all database operations.

## Configuration Helpers

```python
from core_db.config.loader import get_config_dir, get_db_config_path, get_config_info

config_dir = get_config_dir()           # Path to config directory
db_path = get_db_config_path()          # Path to db_config.yaml
info = get_config_info()                # Dict with all resolved paths
```
