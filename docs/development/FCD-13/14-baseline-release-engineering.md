# FCD-13 · Document 14 — Baseline Release Engineering

## 1. Objective
Specifies the release packaging, versioning strategy, cryptographic integrity, and artifact publication procedures for the Menu-It platform foundational baseline.

---

## 2. Release Identity & Semantic Versioning

- **Product:** Menu-It — Restaurant SaaS Platform
- **Release Version:** `v0.1.0`
- **Release Classification:** Pre-1.0 Foundational Platform Baseline
- **Milestone:** FCD-13 (Platform Foundation Completion)
- **Target Git Tag:** `v0.1.0`

### Semantic Versioning Rationale
As mandated by architectural decision `FCD13-ADR-011`, the baseline is tagged as `v0.1.0` rather than `v1.0.0` to preserve semantic accuracy:
- `v0.1.0` proves the technical platform foundation (multi-tenancy, authentication, persistence, async processing, UI design tokens, CI/CD, and deployment) is integrated and validated.
- `v1.0.0` is reserved for the initial customer-facing commercial release following completion of core business domains (organization management, menu builder, live ordering, and billing).

---

## 3. Release Package Composition

The release bundle is structured in the repository under `release/`:
```
release/
├── RELEASE_NOTES.md          # Comprehensive executive & technical release notes
├── RELEASE_MANIFEST.json       # Machine-readable provenance, test evidence & artifact digests
├── CHECKSUMS.txt               # SHA-256 cryptographic hashes of all release documents
└── DEPLOYMENT_REFERENCE.md    # Operating guide, environment configuration, container models
```

---

## 4. Release Tagging & Integrity Workflow

```powershell
# 1. Verify working tree is clean
git status --short

# 2. Verify all quality gates pass
python -m pytest apps/api/tests -q
pnpm test
python tests/deployment/smoke.py --in-process

# 3. Create annotated cryptographic tag
git tag -a v0.1.0 -m "Menu-It foundational platform baseline (FCD-13)"

# 4. Publish tag to remote
git push origin v0.1.0
```

---

## 5. Artifact Digest & Provenance Reference
The container images and manifest reference:
- API Image: `ghcr.io/sahilkhutey/menu-it/api:0.1.0`
- Customer Web: `ghcr.io/sahilkhutey/menu-it/web:0.1.0`
- Admin Portal: `ghcr.io/sahilkhutey/menu-it/admin:0.1.0`
- SHA256 Checksums recorded in [release/CHECKSUMS.txt](file:///c:/Users/ASUS/Documents/Menu-it/release/CHECKSUMS.txt).
