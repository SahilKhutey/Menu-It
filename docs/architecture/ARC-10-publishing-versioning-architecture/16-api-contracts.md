# ARC-10 §16: API Contracts & Specifications
**Canonical REST Endpoints (ARC-07 & ARC-10)**

## 1. Endpoints
- `POST /api/v1/menus/{menu_id}/validate`: Validates current draft for publication readiness.
- `GET /api/v1/menus/{menu_id}/publication-readiness`: Returns readiness report.
- `POST /api/v1/menus/{menu_id}/publish`: Creates and activates a new publication version.
- `GET /api/v1/menus/{menu_id}/publications`: Lists version history with statuses.
- `GET /api/v1/menus/{menu_id}/publications/{pub_id}`: Gets publication metadata.
- `GET /api/v1/menus/{menu_id}/publications/{pub_id}/snapshot`: Authorized full snapshot payload inspection.
- `POST /api/v1/menus/{menu_id}/publications/{pub_id}/rollback`: Reactivates historical snapshot.
- `GET /api/v1/menus/{menu_id}/active-publication`: Retrieves active publication metadata.
- `GET /api/v1/menus/{menu_id}/publication-operations/{op_id}`: Tracks operation status.
- `POST /api/v1/menus/{menu_id}/publication-schedules`: Schedules future publication.
- `DELETE /api/v1/menus/{menu_id}/publication-schedules/{sched_id}`: Cancels scheduled publication.
- `GET /api/v1/menus/{menu_id}/publication-audit`: Retrieves audit history.
