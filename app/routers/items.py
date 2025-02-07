from fastapi import APIRouter
from app.db import query_db
# from dotenv import load_dotenv
import os
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

@router.get("/get_all_items")
async def get_all_items():
    try:
        logger.info("Entering route...")
        query = f"select * from {os.environ.get('DB_DEV_TABLE_ITEMS')}"
        logger.info("Query ready and running...")
        result = query_db(sql=query)
        logger.info("Done")
        return result
    except Exception as e   :
        raise


@router.get('/categories')
async def test_route():
    return "it"


@router.get("/itemss")
def get_users():
    """
    Fetch all users from the database.
    """
    sql = "select * from dev_tg_users;"
    return query_db(sql)
