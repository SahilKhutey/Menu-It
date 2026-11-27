# FCD-09 §10 — Notification Channel Adapters

## 1. Channel Adapter Protocol

Every delivery channel implements `NotificationChannelAdapter`:

```python
class NotificationChannelAdapter(Protocol):
    async def send(self, message: NotificationMessage) -> NotificationResult: ...
```

---

## 2. Email Adapter & Providers

`EmailNotificationAdapter` renders the requested template and hands off the rendered email to an `EmailProvider`:
- **`ConsoleEmailProvider`:** Logs email subject, recipient, and plain-text body to application logs (default for local development).
- **`InMemoryEmailProvider`:** Records emails in memory for unit and integration testing.
- **Future `SmtpEmailProvider`:** Sends emails via standard SMTP or transactional mail APIs (SendGrid, AWS SES, Resend).

---

## 3. In-App Notification Delivery

For the `IN_APP` channel, `NotificationService` directly renders the localized title and body text, inserting a record into the `notifications` PostgreSQL table for the recipient user.
