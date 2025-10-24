# Add this import at the top
from api.utils.rate_limiter import limiter
from fastapi import Request

# Then add @limiter.limit() decorators to endpoints
