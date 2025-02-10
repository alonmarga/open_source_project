from pydantic import BaseModel

class Item(BaseModel):
    item_id: int
    product_name: str
    product_id: str
    category_id : int
    brand : str
    price: float
