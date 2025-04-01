from fastapi import APIRouter

from backend.app.api.v1.endpoints import auth

# Create API router for v1
api_router = APIRouter()

# Include individual endpoint routers
api_router.include_router(auth.router, prefix="/auth")