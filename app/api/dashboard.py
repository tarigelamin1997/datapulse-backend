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

from fastapi import Query
from sqlalchemy import func, cast, Date
from datetime import date
from typing import List, Optional

@router.get("/profit-over-time")
def get_profit_over_time(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    query = db.query(
        cast(Sale.date, Date).label("date"),
        func.sum(Sale.quantity * Sale.unit_price).label("revenue"),
        func.sum(Sale.quantity * Sale.cost_price).label("cost"),
        func.sum((Sale.quantity * (Sale.unit_price - Sale.cost_price))).label("profit")
    ).filter(Sale.user_id == current_user.id)

    if start_date:
        query = query.filter(Sale.date >= start_date)
    if end_date:
        query = query.filter(Sale.date <= end_date)

    query = query.group_by(cast(Sale.date, Date)).order_by("date")

    results = query.all()

    return [
        {
            "date": row.date.isoformat(),
            "revenue": float(row.revenue),
            "cost": float(row.cost),
            "profit": float(row.profit)
        }
        for row in results
    ]
