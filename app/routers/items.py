from fastapi import APIRouter
from app.db import query_db

router = APIRouter()

@router.get("/")
def get_users():
    return {"message": "List of items"}


@router.get('/item')
def test_route():
    return "it"


@router.get("/itemss")
def get_users():
    """
    Fetch all users from the database.
    """
    sql = "select * from dev_tg_users;"
    return query_db(sql)
