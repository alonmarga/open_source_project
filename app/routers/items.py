from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_users():
    return {"message": "List of items"}


@router.get('/item')
def test_route():
    return "item"