# Menu-It — Environment & Configuration Standards

**Document ID:** FCD01-DOC-05  
**Phase:** FCD-01 Development Environment & Repository Foundation  
**Audience:** All Developers, DevOps Engineers, and Security Reviewers  

---

## 1. Environment Topology

Menu-It enforces strict separation across four distinct environments:

| Environment | Purpose | Database | Caching | Secret Injection |
| :--- | :--- | :--- | :--- | :--- |
| **Development** | Local engineering and feature iteration | Local PostgreSQL (Docker) | Local Redis / In-memory | Local `.env` (git-ignored) |
| **Testing** | Automated CI/CD quality gates & test suites | Isolated test DB / SQLite | Mock / In-memory | GitHub Actions secrets |
| **Staging** | Pre-production validation and load testing | Managed PostgreSQL RDS | Managed Redis cluster | Cloud KMS / Vault |
| **Production** | Live tenant operations and public diner traffic | High-availability PostgreSQL RDS | Multi-AZ Redis cluster | Cloud KMS / Runtime IAM |

---

## 2. Secrets Management & Protection Rules

1. **Never Commit Actual Secrets:** Real passwords, private keys, database credentials, and API tokens must never be committed to Git.
2. **Template Only:** Only `.env.example` is committed to version control.
3. **Automatic Redaction:** Logging frameworks must redact passwords, auth tokens, and session cookies (`***`).
4. **Environment-Specific Secrets:** Credentials used in development must never be reused in staging or production.
5. **Startup Validation:** Missing required production environment variables must cause immediate startup failure (`SystemExit` / `ValueError`) rather than silent degradation.

---

## 3. Environment Variable Catalogue

### Core Application
| Variable | Description | Default (Dev) | Required in Prod? |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | Environment identifier (`development`, `staging`, `production`) | `development` | Yes |
| `APP_NAME` | Service display name | `Menu-It` | No |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `DEBUG` | Yes |
| `SECRET_KEY` | Symmetric encryption key for sessions / cookies | `dev-insecure-secret-key-replace` | Yes |

### Database Configuration
| Variable | Description | Default (Dev) | Required in Prod? |
| :--- | :--- | :--- | :--- |
| `POSTGRES_DB` | PostgreSQL database name | `menu_it_dev` | Yes |
| `POSTGRES_USER` | PostgreSQL master user | `menu_it` | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL master password | *Secret* | Yes |
| `DATABASE_HOST` | Database host address | `localhost` | Yes |
| `DATABASE_PORT` | Database connection port | `5432` | Yes |
| `DATABASE_URL` | Full async SQLAlchemy connection URI | *Constructed* | Yes |

### Network & Ports
| Variable | Description | Default (Dev) | Required in Prod? |
| :--- | :--- | :--- | :--- |
| `FRONTEND_PORT` | Port for customer Next.js web application | `3000` | No |
| `BACKEND_PORT` | Port for FastAPI REST backend | `8000` | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000` | Yes |

---

## 4. Local Environment Setup

1. Copy the template:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Edit `.env` and configure a unique development password:
   ```ini
   POSTGRES_PASSWORD=your_secure_dev_password_here
   ```
3. Verify that Git ignores your `.env`:
   ```powershell
   git check-ignore .env
   # Expected output: .env
   ```
