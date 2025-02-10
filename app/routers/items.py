from fastapi import APIRouter
from app.db import *
import os
from utils.logger import setup_logger
from app.models.items_models import Item

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
    except Exception as e:
        logger.error(e)
        return {f"Error has occurred: {str(e)}"}


@router.get('/categories')
async def get_all_categories():
    try:
        logger.info("Entering route...")
        query = f"select * from {os.environ.get('DB_DEV_TABLE_CATEGORIES')}"
        logger.info("Query ready and running...")
        result = query_db(sql=query)
        logger.info("Done")
        return result
    except Exception as e:
        logger.error(e)
        return {f"Error has occurred: {str(e)}"}

@router.post('/create_new_item')
async def create_an_item(item:Item):
    item_dict = item.model_dump()
    columns = ', '.join(item_dict.keys())
    param_placeholders = ', '.join(f':{key}' for key in item_dict.keys())

    query = f"INSERT INTO {os.environ.get('DB_DEV_TABLE_ITEMS')} ({columns}) VALUES ({param_placeholders})"
    logger.info(query)
    return item
