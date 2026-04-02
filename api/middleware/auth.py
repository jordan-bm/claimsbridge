# api/middleware/auth.py

import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


EXCLUDED_PATHS = {"/health", "/"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        expected_key = os.getenv("API_KEY")

        if not expected_key:
            # Fail open with a warning if API_KEY isn't configured — don't crash the app
            import logging
            logging.getLogger(__name__).warning("API_KEY not set in environment — auth is disabled")
            return await call_next(request)

        if api_key != expected_key:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing API key"}
            )

        return await call_next(request)