from fastapi import APIRouter
from app.routers import items  # Import the users router

# Create a centralized router
api_router = APIRouter(prefix='/api')

# Include individual routers
api_router.include_router(items.router, prefix="/items")
