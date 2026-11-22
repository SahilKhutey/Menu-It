# ARC-10 §20: Frontend Publishing Experience
**Next.js Dashboard Components & UX Architecture**

## 1. Feature Components
Located in `frontend/src/features/publishing/`:
- `ReadinessPanel`: Real-time visual indicator of current active version, readiness state, and error counts.
- `ValidationReportView`: Detailed diagnostics list with severity badges and error code paths.
- `PublishDialog`: Confirmation dialog displaying draft revision, new version number, and optional changelog note.
- `VersionHistoryTable`: Comprehensive table of all historical publications with rollback actions.
- `RollbackDialog`: Guarded confirmation dialog requiring mandatory audit reason.

## 2. Dashboard Route
Mounted at `/app/menus/[menuId]/publishing` with 92 kB First Load JS.
