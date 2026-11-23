# Runbook: Failed Deployment & Fast Rollback
**ModularMenu Emergency Runbook**

## 1. Symptoms
- Post-deployment smoke tests fail (`bash infrastructure/scripts/smoke-test.sh`).
- High 5xx error rate following a new release.

## 2. Fast Rollback Procedure
```bash
# 1. Revert compose stack to previous release image tag
export PREVIOUS_TAG="v1.0.0-previous"
docker compose -f compose.yaml -f infrastructure/compose/compose.production.yaml pull
docker compose -f compose.yaml -f infrastructure/compose/compose.production.yaml up -d

# 2. Run smoke tests on restored version
bash infrastructure/scripts/smoke-test.sh
```\n