---
name: core-db
description: Guides writing data access code and configuring projects using the core-db async database library.
version: 1.0.0
author: composeLab
triggers:
  - "use core-db"
  - "write a repository with core-db"
  - "set up core-db in my project"
  - "create a database model"
  - "query the database"
tags:
  - database
  - python
  - internal
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: true
---

# core-db

Assists with writing async data access code using the core-db library (Repository Pattern, Unit of Work, CQRS). Covers model definitions, read/write operations, configuration, and error handling.

## Workflow: Write Data Access Code

### Step 1: Understand the Task

Identify what the user needs: a new model, a query, a write operation, configuration, or a combination. Clarify entity names, fields, and relationships if ambiguous.

### Step 2: Write the Code

Consult [API Reference](references/api-reference.md) for all core-db classes, methods, and filter operators.

For model definitions, follow the BaseModal inheritance pattern with SQLAlchemy 2.0+ `Mapped` type hints. All models inherit `id`, `created_at`, `updated_at`, and `message_id` from BaseModal automatically — do not redeclare these fields.

For write operations, use `UnitOfWork` as an async context manager. Always call `await uow.commit()` before the context exits. Access operations through `uow.repo`.

For read operations, use `ViewManager` as an async context manager. This uses a separate connection pool optimized for reads (CQRS pattern).

For pagination, use cursor-based pagination via the `list()` method with `limit`, `order_by`, and `cursor` parameters.

### Step 3: Handle Errors

Consult [Error Handling](references/error-handling.md) for the exception hierarchy and patterns. Catch specific exceptions (`EntityNotFoundException`, `DuplicateEntityException`) rather than the base `CoreDBException`.

### Step 4: Review

Verify the code uses async/await consistently, commits transactions, and handles expected error cases. Present the result to the user.

## Workflow: Configure core-db

### Step 1: Determine the Database

Identify whether the project uses PostgreSQL or SQLite. PostgreSQL is the production default; SQLite is common for local development and testing.

### Step 2: Set Up Configuration

Consult [Configuration](references/configuration.md) for the YAML config format and environment variable setup. Create or update `db_config.yaml` with connection details. Set the `CONFIG_PATH` environment variable to point to the config directory.

### Step 3: Verify

Confirm the configuration file parses correctly and connection parameters are appropriate for the target environment (pool sizes, timeouts).
