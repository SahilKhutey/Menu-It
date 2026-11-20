# 11 — Repository Pattern and Unit of Work

## 1. Scoped Repositories

All tenant repository operations mandate explicit `TenantContext` passing:
`menu_repo.get_by_id(context, menu_id)`

Direct primary key lookups without tenant scoping (`session.get(Menu, id)`) are strictly prohibited.

## 2. Unit of Work

`SqlAlchemyUnitOfWork` coordinates transactional boundaries and binds the transaction-local PostgreSQL tenant setting upon entry, cleaning it up upon exit.
