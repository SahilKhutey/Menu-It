# Snapshot Integrity Guide
**Cryptographic SHA-256 Hashing Specifications**

## Verification Method
Every snapshot is serialized using canonical JSON (sorted keys, compact separators, UTF-8 encoded).
Any modification to dish names, prices, or themes produces a completely different SHA-256 digest, making tampering impossible to hide.
