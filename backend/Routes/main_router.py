from fastapi import APIRouter
from .travel_router import router as travel_router

# Create main router
main_router = APIRouter()

# Include all sub-routers
main_router.include_router(travel_router) 