from fastapi import APIRouter
from app.db import *
import os
from utils.logger import setup_logger
from app.models.items_models import CreateItem, DeleteItem, UpdateItem

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
async def create_an_item(item:CreateItem):
    try:
        item_dict = item.model_dump()
        logger.info(f"Item dict: {item_dict}")
        columns = ', '.join(item_dict.keys())
        param_placeholders = ', '.join(f':{key}' for key in item_dict.keys())

        query = f"INSERT INTO {os.environ.get('DB_DEV_TABLE_ITEMS')} ({columns}) VALUES ({param_placeholders})"
        insert_db(sql=query,parameters=item_dict)
        return {"Item created successfully!"}
    except Exception as e:
        logger.error(e)
        return {f"Error has occurred: {str(e)}"}


@router.delete('/delete_item')
async def delete_item(item: DeleteItem):
    try:
        item_dict = item.model_dump()
        logger.info(f"Item dict: {item_dict}")

        where_conditions = ' AND '.join(f"{key} = :{key}" for key in item_dict.keys())
        query = f"DELETE FROM {os.environ.get('DB_DEV_TABLE_ITEMS')} WHERE {where_conditions}"

        insert_db(sql=query, parameters=item_dict)
        return {"Item deleted successfully!"}
    except Exception as e:
        logger.error(e)
        return {f"Error has occurred: {str(e)}"}


@router.put('/update_item')
async def update_item(item: UpdateItem):
    try:
        item_dict = item.model_dump(exclude_unset=True)
        logger.info(f"Item dict: {item_dict}")

        # First check if item exists
        check_query = f"SELECT item_id FROM {os.environ.get('DB_DEV_TABLE_ITEMS')} WHERE item_id = :item_id"
        exists = insert_db(sql=check_query, parameters={'item_id': item_dict['item_id']}, returning=True)

        if not exists:
            return {"message": f"Item with id {item_dict['item_id']} not found"}

        # If item exists, proceed with update
        set_values = ', '.join(f"{key} = :{key}" for key in item_dict.keys())
        query = f"UPDATE {os.environ.get('DB_DEV_TABLE_ITEMS')} SET {set_values} WHERE item_id = :item_id"

        insert_db(sql=query, parameters=item_dict)
        return {"Item updated successfully!"}
    except Exception as e:
        logger.error(e)
        return {f"Error has occurred: {str(e)}"}