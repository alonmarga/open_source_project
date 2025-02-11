from fastapi import APIRouter
from fastapi.params import Depends

from app.db import query_db
from .auth import require_read,require_write, require_admin,require_super

router = APIRouter()

@router.get("/count")
def get_users(user = Depends(require_super)):
    """
    Fetch all users from the database.
    """
    sql = "SELECT count(*) FROM dev_tg_users;"
    return query_db(sql)