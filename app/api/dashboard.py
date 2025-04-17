from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.auth_handler import get_current_user
from app.db.database import SessionLocal
from app.db.sales_model import Sale
from app.db.user_model import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/kpi")
def get_kpi_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sales = db.query(Sale).filter(Sale.user_id == current_user.id).all()

    total_revenue = sum(s.quantity * s.unit_price for s in sales)
    total_cost = sum(s.quantity * s.cost_price for s in sales)
    total_profit = total_revenue - total_cost
    margin_percent = (total_profit / total_revenue * 100) if total_revenue else 0
    total_sales = len(sales)

    return {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "margin_percent": round(margin_percent, 2),
        "total_sales_count": total_sales
    }
