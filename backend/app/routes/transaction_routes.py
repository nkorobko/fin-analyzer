"""API routes for transactions"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models import Transaction, Category, Account
from app.schemas import Transaction as TransactionSchema

router = APIRouter()

@router.get("/", response_model=List[TransactionSchema])
async def get_transactions(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in description/merchant"),
    min_amount: Optional[float] = Query(None, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    is_categorized: Optional[bool] = Query(None, description="Filter by categorization status"),
    sort_by: str = Query("date", description="Sort field (date, amount, description)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination limit"),
    db: Session = Depends(get_db)
):
    """
    Get transactions with filtering, sorting, and pagination
    
    **Filters:**
    - account_id: Filter by account
    - category_id: Filter by category
    - start_date/end_date: Date range filter
    - search: Full-text search in description/merchant
    - min_amount/max_amount: Amount range filter
    - is_categorized: Show only categorized/uncategorized transactions
    
    **Sorting:**
    - sort_by: date, amount, description, merchant, category_id
    - sort_order: asc or desc
    
    **Pagination:**
    - skip: Number of records to skip
    - limit: Max records to return (default 100, max 1000)
    """
    query = db.query(Transaction)
    
    # Apply filters
    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)
    
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(search_pattern),
                Transaction.merchant.ilike(search_pattern)
            )
        )
    
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    
    if is_categorized is not None:
        query = query.filter(Transaction.is_categorized == is_categorized)
    
    # Apply sorting
    sort_field = getattr(Transaction, sort_by, Transaction.date)
    if sort_order.lower() == 'desc':
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    transactions = query.all()
    return transactions


@router.get("/stats")
async def get_transaction_stats(
    account_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get transaction statistics
    
    Returns:
    - Total count
    - Total income (positive amounts)
    - Total expenses (negative amounts)
    - Net amount
    - Categorized/uncategorized counts
    """
    query = db.query(Transaction)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.all()
    
    total_count = len(transactions)
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    net_amount = sum(t.amount for t in transactions)
    categorized_count = sum(1 for t in transactions if t.is_categorized)
    uncategorized_count = total_count - categorized_count
    
    return {
        "total_count": total_count,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_amount": net_amount,
        "categorized_count": categorized_count,
        "uncategorized_count": uncategorized_count,
    }


@router.get("/{transaction_id}", response_model=TransactionSchema)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a single transaction by ID"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@router.patch("/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    category_id: Optional[int] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update transaction fields
    
    Allows updating:
    - category_id: Manually categorize transaction
    - notes: Add user notes
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if category_id is not None:
        # Validate category exists
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        
        transaction.category_id = category_id
        transaction.is_categorized = True
        transaction.categorization_method = "manual"
        transaction.categorization_confidence = 1.0
    
    if notes is not None:
        transaction.notes = notes
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    
    return {"success": True, "message": "Transaction deleted"}
