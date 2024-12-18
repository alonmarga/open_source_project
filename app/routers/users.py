# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.models import User
# from app.db.connection import get_db
#
# router = APIRouter()
#
#
# @router.get('/test')
# def test_route():
#     return "test"
#
# @router.get("/")
# def get_users(db: Session = Depends(get_db)):
#     """
#     Retrieve all users from the database.
#     """
#     users = db.query(User).all()
#     return users
#
#
#
#
# @router.get("/")
# def get_users(db: Session = Depends(get_db)):
#     """
#     Retrieve all users from the database.
#     """
#     users = db.query(User).all()
#     return users
#
# @router.get("/{user_id}")
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     """
#     Retrieve a single user by ID.
#     """
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
