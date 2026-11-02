"""Security Headers Middleware.

Architectural and Security Rationale:
- District administration documents contain high-sensitivity Citizen PII (civil registration,
  birth certificates, citizen identification).
- This middleware guarantees that every response leaving the FastAPI service has defensive
  headers applied to protect against Clickjacking, Cross-Site Scripting (XSS), MIME-sniffing,
  and unauthorized proxy/browser caching.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces hardened HTTP response security headers across all endpoints."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response: Response = await call_next(request)

        # Prevent framing / Clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing attacks
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enforce HTTPS transport security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Restrict referrer information leakage across boundaries
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Zero-Data-Retention baseline: instruct intermediate proxies & clients never to cache
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        # Hardware and API permission restrictions
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Baseline Content Security Policy (allows API JSON payloads while forbidding inline rogue scripts)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self';"
        )

        return response
