# 13. External Integration Architecture

## 1. Provider Adapter Pattern
External systems (Email, S3 Object Storage, Payment Gateways) are abstracted behind abstract service protocols:
- `EmailService` -> `ConsoleEmailProvider` (dev/test), `SendGridProvider` / `SESProvider` (prod).
- `StorageService` -> `LocalStorageProvider` (dev/test), `S3CompatibleStorageProvider` (prod).
