from fastapi import APIRouter
from app.routers import items  # Import the users router
from app.routers import users
from app.routers import auth

# Create a centralized router
api_router = APIRouter()

# Include individual routers
api_router.include_router(items.router, prefix="/items")
api_router.include_router(users.router, prefix='/users')