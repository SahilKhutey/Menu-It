# Customer-Hosted Installation Guide (Turnkey Appliance)
**ModularMenu Operational Documentation**

## 1. System Requirements
- Host OS: Ubuntu 22.04 LTS / Debian 12 / Docker-enabled Linux.
- Minimum Specs: 2 vCPU, 4 GB RAM, 20 GB available disk space.
- Open Ports: Port 80 (HTTP) and Port 443 (HTTPS) only.

## 2. Single-Command Turnkey Installation
```bash
# Run the automated installer
curl -fsSL https://raw.githubusercontent.com/SahilKhutey/Menu-It/main/infrastructure/scripts/install-customer-hosted.sh | bash
```

## 3. Post-Installation Verification
1. Access the web interface at `https://<server-ip>/`.
2. Confirm health status: `curl -k https://<server-ip>/health/live`.
3. Complete initial platform administrator onboarding.\n