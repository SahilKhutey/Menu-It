# FCD-05 — Credential Management & Password Security

## 1. Argon2id Password Hashing Specification

Menu-It utilizes **Argon2id** (the hybrid version of Argon2, winner of the Password Hashing Competition) as the primary algorithm for password hashing. Argon2id provides state-of-the-art resistance against both side-channel attacks and GPU/ASIC brute-force cracking.

### Cryptographic Configuration Parameters

| Parameter | Value | Rationale |
|---|---|---|
| Algorithm | `Argon2id` (`v=19`) | Recommended by OWASP and IETF RFC 9106 |
| Time Cost (`t`) | `3` iterations | Computational work factor |
| Memory Cost (`m`) | `65,536 KiB` (64 MiB) | High memory-hardness resisting parallel GPU cracking |
| Parallelism (`p`) | `2` lanes / threads | Optimized for modern multi-core application runtimes |
| Salt Length | `16` bytes (128 bits) | Cryptographically secure random salt generated via `os.urandom` |
| Hash Length | `32` bytes (256 bits) | Output digest length |

Implementation: [hashing.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/src/menu_it/credentials/hashing.py)

---

## 2. Timing Attack Mitigation

To prevent attackers from enumerating registered email addresses by measuring server response times during login, Menu-It executes dummy verification work if the target user account does not exist:

```python
# Precomputed dummy hash for constant-time comparison when email is not found
_DUMMY_HASH = password_hasher.hash("dummy-nonexistent-user-timing-mitigation-password")

def perform_dummy_verification(password: str) -> None:
    with contextlib.suppress(Exception):
        password_hasher.verify(_DUMMY_HASH, password)
```
This ensures an attacker observing HTTP response times cannot distinguish between an invalid email address and an invalid password.

---

## 3. Password Complexity Policy

Menu-It enforces NIST SP 800-63B guidelines prioritizing length over arbitrary character sets:
- **Minimum length:** 12 characters.
- **Maximum length:** 128 characters.
- **Surrounding whitespace:** Disallowed (prevents inadvertent copy-paste whitespace errors).
- **Control characters:** Disallowed (ASCII `0x00`-`0x1F`, `0x7F`).
- **Complexity rules:** No mandatory uppercase/symbol requirements that degrade memorability and lead to predictable substitutions (e.g. `P@ssword1`).
