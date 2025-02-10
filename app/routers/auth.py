from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db import query_db
from utils.logger import setup_logger

security = HTTPBearer()
logger = setup_logger(__name__)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        token_dict = {"token": token}
        logger.info(f"Checking token: {token[:10]}...")

        sql = """
            SELECT u.id, u.telegram_id as tg_id, u.role_id,
                   r.can_read, r.can_write, r.can_update, r.can_delete, r.is_admin
            FROM dev_tg_users u
            JOIN dev_roles r ON u.role_id = r.id
            WHERE u.access_token = :token
        """
        user = query_db(sql, token_dict, fetchone=True)

        if not user:
            logger.warning(f"No user found for token: {token[:10]}...")
            raise HTTPException(status_code=401, detail="Invalid token")

        return user

    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def require_permission(permission: str):
    async def permission_checker(user=Depends(get_current_user)):
        if permission == 'admin' and not user['is_admin']:
            raise HTTPException(status_code=403, detail="Admin access required")

        if not user[f'can_{permission}']:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission}"
            )
        return user

    return permission_checker


# Convenience functions for common checks
require_admin = require_permission('admin')
require_read = require_permission('read')
require_write = require_permission('write')
require_update = require_permission('update')
require_delete = require_permission('delete')