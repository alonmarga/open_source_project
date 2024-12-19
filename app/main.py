import fastapi
from fastapi_offline import FastAPIOffline
from app.routers import api_router  # Import the centralized router

app = FastAPIOffline(title ='test')

# Include the API router
api = fastapi.APIRouter()
app.include_router(api_router)


