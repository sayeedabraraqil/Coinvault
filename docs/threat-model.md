# COINVAULT Threat Model & Security Posture
*Cryptographic & Behavioral Security Specifications*

---

## 1. Executive Summary & Asset Classification
COINVAULT handles competitive esports wealth telemetry, user credentials, and browser extension API tokens. The platform is designed under a **Zero-Trust Input** posture: since eFootball coins can be self-reported, the core integrity threat is intentional or automated fraudulent inflation of leaderboard rankings.

---

## 2. Threat Matrix & Mitigations

| Threat | Vulnerability Vector | Severity | Architectural Mitigation |
|---|---|---|---|
| **Leaderboard Inflation** | Fabricated balance entries entered to gain top ranks | High | **Statistical Outlier Quarantine**: Jumps > 75k coins in < 6h or exceeding Z-Score > 4.0 are auto-flagged and excluded from growth leaderboards until manually cleared by an administrator. |
| **API Token Hijacking** | Leaked client token from browser | High | **SHA-256 Hashing**: Tokens are generated with 32-byte cryptographic entropy (`cv_...`) and stored strictly as salted SHA-256 hashes. Raw tokens cannot be retrieved from database dumps. Revocation is instantaneous. |
| **Tampermonkey Spoofing** | User tampering with the DOM script to send false amounts | Medium | While userscript entries carry the "Verified via script" badge, all entries must still pass through server-side anomaly checks and rate limiting. The platform explicitly communicates DOM limits and maintains an immutable audit log. |
| **Malicious File Uploads** | Web shells or image bombs disguised as profile avatars | Critical | Multi-stage image validation: file extensions are strictly whitelisted, byte magic checked via Pillow (`Image.open() + img.verify()`), and the image is converted to WebP with LANCZOS downsampling to strip EXIF and malicious payloads. |
| **Brute Force & Flooding** | Credential stuffing or DoS on the balance log endpoint | Medium | **Flask-Limiter**: Login is restricted to 30 requests/hour; coin logging to 60 requests/hour; script API to 120/hour. Repeated duplicate payloads within 10-30 seconds are rejected. |
| **Cross-Site Request Forgery** | Malicious sites triggering balance changes or token creation | High | **Flask-WTF CSRF Protection**: Every HTML mutation form enforces cryptographically signed, rotating CSRF tokens. External API endpoints require `Authorization: Bearer` headers. |
| **Content Injection & Clickjacking** | XSS or iframe embedding | High | Strict HTTP response headers: `Content-Security-Policy`, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, and `Referrer-Policy: strict-origin-when-cross-origin`. |

---

## 3. Incident Response & Moderation
- **Immutable Ledger**: Entries are never destructively overwritten. An archive creates a record with `is_deleted = True` and timestamp in `AuditLog`.
- **Administrative Override**: Admins have instantaneous controls to quarantine suspicious entries, dismiss false positives, or ban malicious users from the global platform.
