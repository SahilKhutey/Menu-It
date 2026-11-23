# Local Development Setup Guide
**ModularMenu Operational Documentation**

## 1. Prerequisites
- Docker Engine >= 24.0 and Docker Compose >= 2.20
- Python 3.12+ and Poetry / venv
- Node.js 20+ and pnpm >= 9.0

## 2. Initial Setup
```bash
# Clone the repository
git clone https://github.com/SahilKhutey/Menu-It.git
cd Menu-It

# Copy local development configuration
cp .env.example .env

# Install backend dependencies
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
pnpm install
```

## 3. Starting the Local Stack
```bash
# From repository root
docker compose -f compose.yaml -f compose.dev.yaml up -d
```
- Frontend UI: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health/live`\n