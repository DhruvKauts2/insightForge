"""
Rate limit models
"""
from pydantic import BaseModel
from typing import Optional


class RateLimitInfo(BaseModel):
    """Rate limit information"""
    limit: int
    remaining: int
    reset: int  # Unix timestamp
    
    
class RateLimitExceeded(BaseModel):
    """Rate limit exceeded response"""
    error: str = "rate_limit_exceeded"
    message: str
    limit: int
    retry_after: int  # Seconds until reset
