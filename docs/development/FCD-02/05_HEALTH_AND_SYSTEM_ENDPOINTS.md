# FCD-02 — Health & System Runtime Endpoints

## 1. Overview
Menu-It separates process liveness, functional runtime readiness, and system discovery into distinct endpoints under `/api/v1`.

## 2. Endpoint Specifications

### 2.1 `/api/v1/health`
- **Method:** `GET`
- **Purpose:** Primary operational status check for developers and monitoring services.
- **Response Model:** `HealthResponse`
- **Sample Payload:**
  ```json
  {
    "status": "healthy",
    "application": "Menu-It",
    "version": "0.1.0"
  }
  ```

### 2.2 `/api/v1/health/live`
- **Method:** `GET`
- **Purpose:** Kubernetes / Docker container orchestrator liveness probe. Indicates the process is responsive and not deadlocked.
- **Response:** `{"status": "alive"}` (HTTP 200)

### 2.3 `/api/v1/health/ready`
- **Method:** `GET`
- **Purpose:** Readiness probe determining whether the container may receive live traffic.
- **Behavior:**
  - `HTTP 200` with `{"status": "ready", "ready": true}` when `application.state.runtime_ready == True`.
  - `HTTP 503` when runtime is uninitialized or shutting down.

### 2.4 `/api/v1/system/info`
- **Method:** `GET`
- **Purpose:** Non-sensitive system discovery metadata.
- **Sample Payload:**
  ```json
  {
    "application": "Menu-It",
    "version": "0.1.0",
    "environment": "development",
    "api_prefix": "/api/v1"
  }
  ```
- **Security Rule:** Never exposes secrets, internal environment variables, or private infrastructure IP addresses.
