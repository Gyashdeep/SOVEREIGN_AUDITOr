# Security Architecture

## Cryptographic Integrity
The Sovereign Auditor uses a hash-chaining mechanism. Each ledger entry contains:
- `prev_hash`: The SHA-256 hash of the preceding entry.
- `hash`: The current SHA-256 hash of the data + `prev_hash`.
- `signature`: An HMAC-SHA256 signature generated using a private `SECRET_KEY`.

This ensures that any retroactive tampering with the log file results in a broken hash chain that can be identified instantly via the `verify_ledger.py` script.

## Safety & Governance
- **Circuit Breaker:** Any request returning a `risk_score` > 0.8 is hard-blocked at the application layer, independent of the model's output.
- **Environment Isolation:** Secrets are managed via environment variables and should be handled by a secure Vault in production.
