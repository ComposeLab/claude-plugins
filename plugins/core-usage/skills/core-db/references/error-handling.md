# core-db Error Handling

## Exception Hierarchy

All core-db exceptions inherit from `CoreDBException`:

```
CoreDBException
├── DatabaseConnectionException
├── EntityNotFoundException
├── DuplicateEntityException
├── TransactionException
├── ConfigurationException
├── ValidationException
└── IntegrityConstraintException
    ├── ForeignKeyException
    ├── CheckConstraintException
    ├── UniqueConstraintException
    └── NotNullException
```

Import exceptions from `core_db.exceptions`.

## When Each Exception Occurs

**EntityNotFoundException** — Raised when `get_by_id()` or `get()` finds no matching entity. Catch this when a missing entity is an expected possibility.

**DuplicateEntityException** — Raised when inserting an entity that violates a unique constraint (before the database-level error). Catch this around `add()` and `bulk_add()` calls.

**IntegrityConstraintException** and subclasses — Raised when a database constraint is violated. The library automatically parses the raw database error and raises the specific subclass:

- `UniqueConstraintException` — duplicate value on a unique column
- `ForeignKeyException` — referenced entity does not exist or would be orphaned
- `NotNullException` — required column received NULL
- `CheckConstraintException` — CHECK constraint violated

Each integrity exception includes `constraint_name`, `table`, and `column` attributes for programmatic handling.

**TransactionException** — Raised on transaction state errors like double-commit or post-rollback operations.

**DatabaseConnectionException** — Raised when the connection cannot be established or the pool is exhausted.

**ConfigurationException** — Raised when `db_config.yaml` is missing, malformed, or references unknown connections.

## Patterns

### Catch Specific Exceptions

```python
from core_db.exceptions import EntityNotFoundException, DuplicateEntityException

async with UnitOfWork() as uow:
    try:
        await uow.repo.add(User, user)
        await uow.commit()
    except DuplicateEntityException:
        # Handle duplicate email, etc.
        pass
```

### Let Rollback Happen Automatically

When an exception propagates out of the `UnitOfWork` context, the transaction rolls back automatically. There is no need to call `uow.rollback()` explicitly unless catching the exception and continuing within the same context.

### Integrity Error Details

```python
from core_db.exceptions import UniqueConstraintException

try:
    await uow.repo.add(User, user)
    await uow.commit()
except UniqueConstraintException as e:
    print(e.constraint_name)  # e.g. "uq_users_email"
    print(e.table)            # e.g. "users"
    print(e.column)           # e.g. "email"
```
