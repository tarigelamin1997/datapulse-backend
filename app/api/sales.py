from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.sales import SaleCreate
from app.db import sales_model
from app.db.database import SessionLocal
from app.auth.auth_handler import get_current_user
from app.db.user_model import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
def upload_sale(sale: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_sale = sales_model.Sale(
        user_id=current_user.id,
        **sale.dict()
    )
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return {"status": "success", "sale_id": new_sale.id}
