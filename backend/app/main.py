"""
FastAPI main application.
Entry point for EaseForm backend.
"""

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.routers import forms, responses, public_forms
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Configure Rate Limiting
limiter = Limiter(key_func=get_remote_address)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://*.supabase.co; img-src 'self' data: https://*; font-src 'self' https://fonts.gstatic.com;"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# Create FastAPI app
app = FastAPI(
    title="EaseForm API",
    description="Privacy-first form builder backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add Rate Limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add GZip Middleware
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS - MUST be added before routes
# In production, replace localhost origins with actual domain
allowed_origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Add frontend_url from settings if different
if settings.frontend_url not in allowed_origins:
    allowed_origins.append(settings.frontend_url)

# Only add development origins in dev environment
if settings.environment == "development":
    allowed_origins.extend([
        "http://localhost:5500",  # Live Server
        "http://127.0.0.1:5500",
        "http://localhost:3000",  # Common dev ports
        "http://127.0.0.1:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and return JSON response."""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions and return JSON response."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error occurred",
            "detail": str(exc) if settings.environment == "development" else None
        }
    )

# Include routers
# Include routers
app.include_router(forms.router, prefix=settings.api_prefix)
app.include_router(responses.router, prefix=settings.api_prefix)
app.include_router(public_forms.router, prefix=f"{settings.api_prefix}/public/forms")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "EaseForm API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "supabase_configured": bool(settings.supabase_url)
    }


@app.get("/cors-test")
async def cors_test():
    """CORS verification endpoint."""
    return {
        "ok": True,
        "message": "CORS is working!",
        "cors_configured": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == "development" else False
    )
