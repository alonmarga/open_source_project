from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/", summary="Get sample data")
def get_data():
    return {"data": "Sample data", "timestamp": datetime.now()}

@router.get("/info", summary="Get data info")
def get_data_info():
    return {"info": "This route provides sample data info."}