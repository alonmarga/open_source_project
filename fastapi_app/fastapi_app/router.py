from fastapi import APIRouter
from fastapi_app.api.routes.user_routes import router as user_router
from fastapi_app.api.routes.data_routes import router as data_router

api_router = APIRouter()

# Register all routers with prefixes and tags
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(data_router, prefix="/data", tags=["Data"])
