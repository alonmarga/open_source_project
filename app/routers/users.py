from fastapi import APIRouter
from app.db import query

router = APIRouter()

@router.get("/count")
def get_users():
    """
    Fetch all users from the database.
    """
    sql = "SELECT count(*) FROM users;"
    return query(sql)


@router.get("/rownum")
def get_users():
    """
    Fetch all users from the database.
    """
    sql = "SELECT ROW_NUMBER() OVER (ORDER BY id) AS row_number, * FROM users;"
    return query(sql)