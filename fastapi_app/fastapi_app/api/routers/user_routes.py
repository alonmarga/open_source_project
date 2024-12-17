from fastapi import APIRouter
from fastapi_app.models.user_model import User

router = APIRouter()

# In-memory database (for example purposes)
fake_users_db = [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Doe", "email": "jane@example.com"},
]

@router.get("/", summary="Get all users")
def get_users():
    return fake_users_db

@router.get("/{user_id}", summary="Get a user by ID")
def get_user(user_id: int):
    user = next((u for u in fake_users_db if u["id"] == user_id), None)
    if user:
        return user
    return {"error": "User not found"}

@router.post("/", summary="Create a new user")
def create_user(user: User):
    new_user = {"id": len(fake_users_db) + 1, **user.dict()}
    fake_users_db.append(new_user)
    return new_user