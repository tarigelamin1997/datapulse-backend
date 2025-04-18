from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date
from typing import Optional
import calendar
import csv
import io

from weasyprint import HTML
from jinja2 import Template

from app.auth.auth_handler import get_current_user
from app.db.database import SessionLocal
from app.db.sales_model import Sale
from app.db.user_model import User

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ────────────────────────────────────────────────────────────
# /dashboard/kpi
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

# ────────────────────────────────────────────────────────────
# /dashboard/profit-over-time
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

# ────────────────────────────────────────────────────────────
# /dashboard/monthly-summary
@router.get("/monthly-summary")
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    query = db.query(
        func.extract('year', Sale.date).label('year'),
        func.extract('month', Sale.date).label('month'),
        func.sum(Sale.quantity * Sale.unit_price).label("revenue"),
        func.sum(Sale.quantity * Sale.cost_price).label("cost"),
        func.sum((Sale.quantity * (Sale.unit_price - Sale.cost_price))).label("profit")
    ).filter(Sale.user_id == current_user.id)

    if start_date:
        query = query.filter(Sale.date >= start_date)
    if end_date:
        query = query.filter(Sale.date <= end_date)

    query = query.group_by('year', 'month').order_by('year', 'month')
    results = query.all()

    return [
        {
            "year": int(row.year),
            "month_number": int(row.month),
            "month_name": calendar.month_name[int(row.month)],
            "revenue": round(float(row.revenue), 2),
            "cost": round(float(row.cost), 2),
            "profit": round(float(row.profit), 2),
            "profit_margin": round(float(row.profit) / float(row.revenue) * 100, 2) if row.revenue else 0.0
        }
        for row in results
    ]

# ────────────────────────────────────────────────────────────
# /dashboard/export/csv
@router.get("/export/csv")
def export_monthly_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        func.extract('year', Sale.date).label('year'),
        func.extract('month', Sale.date).label('month'),
        func.sum(Sale.quantity * Sale.unit_price).label("revenue"),
        func.sum(Sale.quantity * Sale.cost_price).label("cost"),
        func.sum((Sale.quantity * (Sale.unit_price - Sale.cost_price))).label("profit")
    ).filter(Sale.user_id == current_user.id).group_by('year', 'month').order_by('year', 'month')

    results = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Year", "Month", "Revenue", "Cost", "Profit"])
    for row in results:
        writer.writerow([int(row.year), int(row.month), float(row.revenue), float(row.cost), float(row.profit)])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=monthly_summary.csv"})

# ────────────────────────────────────────────────────────────
# /dashboard/export/pdf
@router.get("/export/pdf")
def export_monthly_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        func.extract('year', Sale.date).label('year'),
        func.extract('month', Sale.date).label('month'),
        func.sum(Sale.quantity * Sale.unit_price).label("revenue"),
        func.sum(Sale.quantity * Sale.cost_price).label("cost"),
        func.sum((Sale.quantity * (Sale.unit_price - Sale.cost_price))).label("profit")
    ).filter(Sale.user_id == current_user.id).group_by('year', 'month').order_by('year', 'month')

    results = query.all()

    html_template = """
    <h1>Monthly Business Summary</h1>
    <table border="1" style="border-collapse: collapse; width: 100%; font-size: 14px;">
        <tr style="background-color: #87ceeb;">
            <th>Year</th>
            <th>Month</th>
            <th>Revenue</th>
            <th>Cost</th>
            <th>Profit</th>
        </tr>
        {% for row in data %}
        <tr>
            <td>{{ row.year }}</td>
            <td>{{ row.month }}</td>
            <td>${{ "%.2f"|format(row.revenue) }}</td>
            <td>${{ "%.2f"|format(row.cost) }}</td>
            <td>${{ "%.2f"|format(row.profit) }}</td>
        </tr>
        {% endfor %}
    </table>
    """

    template = Template(html_template)
    rendered_html = template.render(data=[
        {
            "year": int(row.year),
            "month": int(row.month),
            "revenue": float(row.revenue),
            "cost": float(row.cost),
            "profit": float(row.profit)
        }
        for row in results
    ])

    pdf = HTML(string=rendered_html).write_pdf()
    return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=monthly_summary.pdf"})
