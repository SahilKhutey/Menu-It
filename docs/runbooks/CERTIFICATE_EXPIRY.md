# Runbook: TLS Certificate Expiry & Emergency Renewal
**ModularMenu Emergency Runbook**

## 1. Symptoms
- Browsers show SSL/TLS certificate warnings or expired error.

## 2. Remediation
```bash
# If using Certbot Let's Encrypt
docker compose run --rm certbot renew --force-renewal
docker compose exec proxy nginx -s reload

# If using custom certificates, replace cert/key files and reload proxy
docker compose exec proxy nginx -s reload
```\n