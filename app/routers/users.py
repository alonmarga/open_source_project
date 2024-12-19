from fastapi import APIRouter
from ..db import query

router = APIRouter()

@router.get("/count")
def get_users():
    """
    Fetch all users from the database.
    """
    sql = "SELECT count(*) FROM users;"
    return query(sql)