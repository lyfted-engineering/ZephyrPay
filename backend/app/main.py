from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from backend.app.api.v1 import api_router
from backend.app.core.config import settings
from backend.app.core.errors import BaseZephyrPayError

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("zephyrpay")

# Create FastAPI app
app = FastAPI(
    title=settings.SERVER_NAME,
    description="""
    ZephyrPay API - Crypto-native payment and access management platform for member-only spaces.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Add exception handlers
@app.exception_handler(BaseZephyrPayError)
async def zephyrpay_exception_handler(request: Request, exc: BaseZephyrPayError):
    """Handle ZephyrPay custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {
        "name": settings.SERVER_NAME,
        "version": "0.1.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "v1"
    }