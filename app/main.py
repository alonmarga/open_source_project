from routers.routers import setup_routers  # Import setup_routers from the routers/routers.py file

from fastapi import FastAPI

app = FastAPI()

setup_routers(app)
