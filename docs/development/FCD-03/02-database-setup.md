# FCD-03 — Database Setup & Environment Provisioning

## 1. Overview

Menu-It uses **PostgreSQL 17** as its relational database. This document defines the local provisioning, containerized deployment, environment variables, credentials handling, and connectivity validation procedures.

---

## 2. Docker Compose Configuration

The PostgreSQL container is integrated into `compose.yaml` and `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:17
    container_name: menu-it-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: menu_it
      POSTGRES_USER: menu_it
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-devpassword123}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - menu_it_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -U menu_it -d menu_it
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  menu_it_postgres_data:
```

---

## 3. Environment Configuration & Variables

Environment variables are defined in `.env.example` and consumed by `apps/api/src/menu_it/core/config.py`:

| Variable | Type | Default Value | Purpose |
| :--- | :--- | :--- | :--- |
| `POSTGRES_USER` | string | `menu_it` | PostgreSQL superuser/application user |
| `POSTGRES_PASSWORD` | string | `change_this_local_password` | Local authentication secret |
| `POSTGRES_DB` | string | `menu_it` | Default database name |
| `DATABASE_URL` | string | `postgresql+asyncpg://menu_it:pass@localhost:5432/menu_it` | Async application connection string |
| `DATABASE_TEST_URL` | string | `postgresql+asyncpg://menu_it_test:pass@localhost:5432/menu_it_test` | Dedicated isolated test database |
| `DATABASE_POOL_SIZE` | int | `5` | Steady-state connection pool size |
| `DATABASE_MAX_OVERFLOW`| int | `10` | Temporary surge connection limit |
| `DATABASE_POOL_TIMEOUT` | int | `30` | Seconds to wait before timing out |
| `DATABASE_POOL_RECYCLE` | int | `1800` | Seconds before recycling idle connections |
| `DATABASE_ECHO` | bool | `false` | Echo SQL statements to console |

> [!CAUTION]
> Never log or display `DATABASE_URL` in raw form. Passwords and credentials must remain secret.

---

## 4. Connectivity Verification Script

A standalone diagnostic script is located at [check_database.py](file:///c:/Users/ASUS/Documents/Menu-it/scripts/development/check_database.py):

```bash
# Execute standalone database check
python scripts/development/check_database.py
```

Expected output when running:
```text
Database result: 1
```
