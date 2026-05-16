# ADR-0009: JWT Authentication with HS256

**Date:** 2026-05-16  
**Status:** Accepted

## Context

The API exposes sensitive operations: reading internal log data, managing alert rules, and acknowledging triggered alerts. These endpoints must be accessible only to authenticated users. We need a stateless authentication mechanism that works across multiple Uvicorn worker processes (so no server-side session store is needed) and integrates cleanly with FastAPI's dependency injection system.

## Decision

Use JSON Web Tokens (JWT) signed with HMAC-SHA256 (HS256) for stateless authentication. Passwords are hashed with bcrypt before storage in PostgreSQL. Tokens are issued at `POST /api/v1/auth/token` and expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`). The signing secret is read from `SECRET_KEY` in the environment.

`python-jose[cryptography]` handles token encoding and decoding. FastAPI's `Depends()` mechanism is used to inject the authenticated user into protected route handlers — unauthenticated requests receive a `401 Unauthorized` response.

## Consequences

**Positive**
- Stateless tokens require no session store; any of the four Uvicorn workers can validate any token independently using the shared `SECRET_KEY`.
- bcrypt's adaptive cost factor provides protection against brute-force attacks on the credential store.
- The FastAPI `Depends()` pattern makes it easy to mark individual endpoints as protected with a single decorator.
- 30-minute token expiry limits the window of exposure if a token is leaked.

**Negative**
- HS256 uses a symmetric key: any service that can verify tokens can also issue them. A compromise of `SECRET_KEY` allows minting arbitrary tokens. RS256 (asymmetric) would be safer for a multi-service environment.
- No token revocation mechanism: a logged-out user's token remains valid until expiry. A short TTL mitigates but does not eliminate this.
- The default `SECRET_KEY` in `.env` (`your-secret-key-change-this-in-production`) is dangerously weak; production deployments must rotate this.
- No refresh token flow: users must re-authenticate every 30 minutes, which degrades dashboard usability over long on-call shifts.
- CORS is currently open (`*`), which, combined with JWT in a browser, increases exposure to CSRF-style token theft from XSS.
