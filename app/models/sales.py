from pydantic import BaseModel
from datetime import date

class SaleCreate(BaseModel):
    date: date
    item_name: str
    quantity: int
    unit_price: float
    cost_price: float
