# ARC-10 §8: Version Number Policy
**Deterministic Monotonic Sequencing**

## 1. Rules
1. Version numbering starts at integer `1` upon first successful publication.
2. Each new publication receives `max(version_number) + 1` for that menu.
3. Version numbers are gapless and strictly increasing.
4. Failed publication attempts do not consume a version number.
5. Rollbacks do NOT create a new snapshot or version number; they update the active pointer to an existing version.
6. A subsequent publication following a rollback increments to the next available integer.

## 2. Example Lifecycle
| Operation | Created Version | Active Version |
| :--- | :--- | :--- |
| First publish | v1 | v1 |
| Second publish | v2 | v2 |
| Third publish | v3 | v3 |
| Rollback to v1 | (None) | v1 |
| Publish new edits | v4 | v4 |
