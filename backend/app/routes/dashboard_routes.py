"""API routes for dashboard statistics"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.database import get_db
from app.models import Transaction, Category

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get dashboard overview statistics
    
    Returns:
    - Total income, expenses, net amount
    - Transaction count
    - Average transaction size
    - Categorized percentage
    """
    query = db.query(Transaction)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.all()
    
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    net_amount = total_income - total_expenses
    
    transaction_count = len(transactions)
    categorized_count = sum(1 for t in transactions if t.is_categorized)
    categorized_percentage = (categorized_count / transaction_count * 100) if transaction_count > 0 else 0
    
    avg_income = total_income / sum(1 for t in transactions if t.amount > 0) if any(t.amount > 0 for t in transactions) else 0
    avg_expense = total_expenses / sum(1 for t in transactions if t.amount < 0) if any(t.amount < 0 for t in transactions) else 0
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_amount": net_amount,
        "transaction_count": transaction_count,
        "categorized_count": categorized_count,
        "categorized_percentage": round(categorized_percentage, 1),
        "avg_income": avg_income,
        "avg_expense": avg_expense,
    }

@router.get("/spending-by-category")
async def get_spending_by_category(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    account_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get spending breakdown by category
    
    Returns top N categories by expense amount
    """
    query = db.query(
        Category.id,
        Category.name,
        Category.icon,
        Category.color,
        func.sum(func.abs(Transaction.amount)).label('total')
    ).join(Transaction, Transaction.category_id == Category.id)\
     .filter(Transaction.amount < 0)  # Only expenses
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    results = query.group_by(Category.id)\
                   .order_by(func.sum(func.abs(Transaction.amount)).desc())\
                   .limit(limit)\
                   .all()
    
    categories = []
    for row in results:
        categories.append({
            "id": row.id,
            "name": row.name,
            "icon": row.icon,
            "color": row.color,
            "amount": float(row.total),
        })
    
    return categories

@router.get("/income-vs-expenses")
async def get_income_vs_expenses_trend(
    months: int = Query(6, ge=1, le=24),
    account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get monthly income vs expenses trend
    
    Returns data for the last N months
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 31)
    
    query = db.query(Transaction)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    transactions = query.filter(Transaction.date >= start_date).all()
    
    # Group by month
    monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})
    
    for tx in transactions:
        month_key = tx.date.strftime("%Y-%m")
        if tx.amount > 0:
            monthly_data[month_key]["income"] += tx.amount
        else:
            monthly_data[month_key]["expenses"] += abs(tx.amount)
    
    # Convert to list and sort
    trend = []
    for month, data in sorted(monthly_data.items()):
        trend.append({
            "month": month,
            "month_name": datetime.strptime(month, "%Y-%m").strftime("%b %Y"),
            "income": data["income"],
            "expenses": data["expenses"],
            "net": data["income"] - data["expenses"],
        })
    
    return trend

@router.get("/category-trends")
async def get_category_spending_trends(
    category_id: int,
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """
    Get spending trend for a specific category over time
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 31)
    
    transactions = db.query(Transaction)\
        .filter(Transaction.category_id == category_id)\
        .filter(Transaction.date >= start_date)\
        .all()
    
    # Group by month
    monthly_data = defaultdict(float)
    
    for tx in transactions:
        month_key = tx.date.strftime("%Y-%m")
        monthly_data[month_key] += abs(tx.amount)
    
    # Convert to list
    trend = []
    for month, amount in sorted(monthly_data.items()):
        trend.append({
            "month": month,
            "month_name": datetime.strptime(month, "%Y-%m").strftime("%b %Y"),
            "amount": amount,
        })
    
    return trend

@router.get("/recent-transactions")
async def get_recent_transactions(
    limit: int = Query(10, ge=1, le=50),
    account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get most recent transactions"""
    query = db.query(Transaction).order_by(Transaction.date.desc())
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    transactions = query.limit(limit).all()
    
    return transactions

@router.get("/top-merchants")
async def get_top_merchants(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get top merchants by spending
    
    Only includes expenses (negative amounts)
    """
    query = db.query(
        Transaction.merchant,
        func.count(Transaction.id).label('transaction_count'),
        func.sum(func.abs(Transaction.amount)).label('total_spent')
    ).filter(
        Transaction.merchant != None,
        Transaction.amount < 0
    )
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    results = query.group_by(Transaction.merchant)\
                   .order_by(func.sum(func.abs(Transaction.amount)).desc())\
                   .limit(limit)\
                   .all()
    
    merchants = []
    for row in results:
        merchants.append({
            "merchant": row.merchant,
            "transaction_count": row.transaction_count,
            "total_spent": float(row.total_spent),
        })
    
    return merchants
