# core-db API Reference

## Public Imports

All primary classes are available from `core_db`:

```python
from core_db import UnitOfWork, ViewManager, BaseModal
```

## BaseModal

Base class for all entity models. Inherits from SQLAlchemy's declarative base.

**Inherited fields (do not redeclare):**
- `id: str` — UUID primary key (String(36)), auto-generated
- `created_at: datetime` — Set automatically on creation (UTC)
- `updated_at: datetime | None` — Updated automatically via event listener
- `message_id: str | None` — Optional, for event tracking

**Defining a model:**

```python
from sqlalchemy import Integer, String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core_db import BaseModal

class User(BaseModal):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)

    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )
```

Use SQLAlchemy 2.0+ `Mapped` type hints. Standard constraints (unique, nullable, default, ForeignKey) all work as expected.

## UnitOfWork — Write Operations

Factory function returning an async context manager for transactions.

```python
async with UnitOfWork() as uow:
    # operations via uow.repo
    await uow.commit()
```

Always commit before the context exits. On exception, the transaction rolls back automatically.

### Available Methods on `uow.repo`

| Method | Signature | Description |
|--------|-----------|-------------|
| `add` | `(Model, entity)` | Insert a single entity |
| `update` | `(Model, entity)` | Update a single entity |
| `bulk_add` | `(Model, entities)` | Insert multiple entities |
| `bulk_update` | `(Model, entities)` | Update multiple entities |
| `delete` | `(Model, entity)` | Delete by entity reference |
| `delete_by_id` | `(Model, entity_id)` | Delete by primary key |
| `bulk_delete` | `(Model, ids)` | Delete multiple by IDs |
| `delete_where` | `(Model, **filters)` | Delete matching filter criteria, returns count |
| `upsert` | `(Model, entity, conflict_columns, update_columns)` | Insert or update on conflict |
| `list` | `(Model, limit, order_by, cursor, **filters)` | Paginated query |
| `exists` | `(Model, **filters)` | Check existence |
| `count` | `(Model, **filters)` | Count matching rows |
| `execute` | `(sql_string, params)` | Raw SQL, returns affected row count |

### Write Examples

```python
async with UnitOfWork() as uow:
    # Add
    user = User(name="Alice", email="alice@example.com")
    await uow.repo.add(User, user)

    # Update
    user.name = "Alice B."
    await uow.repo.update(User, user)

    # Upsert (insert or update on email conflict)
    await uow.repo.upsert(
        User, user,
        conflict_columns=["email"],
        update_columns=["name", "age"],
    )

    # Bulk operations
    await uow.repo.bulk_add(User, [user1, user2])
    await uow.repo.bulk_delete(User, [id1, id2])

    # Conditional delete
    deleted_count = await uow.repo.delete_where(User, status="inactive")

    # Raw SQL
    affected = await uow.repo.execute(
        "UPDATE users SET status = :status WHERE age > :age",
        {"status": "senior", "age": 65},
    )

    await uow.commit()
```

## ViewManager — Read Operations

Standalone async context manager for read-only queries. Uses a separate connection pool reserved for reads.

```python
async with ViewManager() as view:
    user = await view.get_by_id(User, some_id)
```

### Available Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_by_id` | `(Model, entity_id)` | Fetch by primary key |
| `get` | `(Model, **filters)` | Fetch single entity matching filters |
| `list` | `(Model, limit, order_by, cursor, **filters)` | Paginated query |
| `exists` | `(Model, **filters)` | Check existence |
| `count` | `(Model, **filters)` | Count matching rows |
| `execute` | `(sql_string, params)` | Raw SQL, returns rows |

### Read Examples

```python
async with ViewManager() as view:
    user = await view.get_by_id(User, user_id)
    user = await view.get(User, email="alice@example.com")
    active_users = await view.list(User, status="active", age__gte=18)
    exists = await view.exists(User, email="alice@example.com")
    count = await view.count(User, age__gte=18)
```

## Filter Operators

Filters use Django-style double-underscore suffixes on keyword arguments.

| Suffix | SQL | Example |
|--------|-----|---------|
| *(none)* | `=` | `age=30` |
| `__gt` | `>` | `age__gt=30` |
| `__gte` | `>=` | `age__gte=30` |
| `__lt` | `<` | `age__lt=30` |
| `__lte` | `<=` | `age__lte=30` |
| `__ne` | `!=` | `status__ne="inactive"` |
| `__in` | `IN` | `id__in=[1, 2, 3]` |
| `__like` | `LIKE` | `name__like="%john%"` |
| `__ilike` | `ILIKE` | `name__ilike="john%"` |
| `__isnull` | `IS NULL` / `IS NOT NULL` | `deleted_at__isnull=True` |

Filters work on both `uow.repo` and `ViewManager` methods that accept `**filters`.

## Cursor-Based Pagination

The `list()` method returns a `CursorPaginationResult`:

```python
@dataclass
class CursorPaginationResult(Generic[T]):
    entities: list[T]
    next_cursor: str | None
    has_next_page: bool
```

**Usage:**

```python
async with ViewManager() as view:
    # First page
    result = await view.list(
        User,
        limit=20,
        order_by=[["created_at", "desc"], ["id", "asc"]],
        status="active",
    )
    users = result.entities

    # Next page
    if result.has_next_page:
        next_page = await view.list(
            User,
            cursor=result.next_cursor,
            limit=20,
            order_by=[["created_at", "desc"], ["id", "asc"]],
            status="active",
        )
```

The cursor is a base64-encoded JSON string. Always pass the same `order_by` and filters when using a cursor from a previous result.
