from fastapi import FastAPI
from routers import users, items

def setup_routers(app: FastAPI):
    """Centralized function to include all routers."""
    # app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(items.router,prefix="/items")
