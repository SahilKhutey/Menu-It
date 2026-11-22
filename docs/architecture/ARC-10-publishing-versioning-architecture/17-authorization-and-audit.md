# ARC-10 §17: Authorization & Audit Architecture
**RBAC Permissions and Tamper-Proof Audit Logging**

## 1. Permission Matrix
| Role | Validate | Publish | Rollback | View History | Approve |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Platform Owner | Yes | Support Only | Support Only | Support Only | Policy |
| Restaurant Owner | Yes | Yes | Yes | Yes | Yes |
| Restaurant Manager | Yes | Yes | Yes | Yes | Configurable |
| Menu Editor | Yes | No | No | Read Only | No |
| Viewer | No | No | No | No | No |

## 2. Audit Trail
All publish, rollback, and schedule mutations record actor ID, client IP, correlation ID, target publication ID, and timestamp.
