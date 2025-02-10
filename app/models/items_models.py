from typing import Optional

from pydantic import BaseModel

class CreateItem(BaseModel):
    item_id: int
    product_name: str
    product_id: str
    category_id : int
    brand : str
    price: float

class DeleteItem(BaseModel):
    item_id: int

class UpdateItem(BaseModel):
    item_id: int
    product_name: Optional[str] = None
    product_id: Optional[str] = None
    brand: Optional[str] = None