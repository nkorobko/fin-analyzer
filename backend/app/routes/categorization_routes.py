"""API routes for categorization"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models import CategorizationRule, Category
from app.services.categorization_service import CategorizationService

router = APIRouter()

class RuleCreate(BaseModel):
    category_id: int
    rule_type: str  # keyword, regex, merchant
    pattern: str
    priority: int = 0

class RuleUpdate(BaseModel):
    category_id: int = None
    rule_type: str = None
    pattern: str = None
    priority: int = None
    is_active: bool = None

@router.get("/rules")
async def get_rules(db: Session = Depends(get_db)):
    """Get all categorization rules"""
    rules = db.query(CategorizationRule).order_by(CategorizationRule.priority.desc()).all()
    return rules

@router.post("/rules")
async def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """Create a new categorization rule"""
    # Validate category exists
    category = db.query(Category).filter(Category.id == rule.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    
    new_rule = CategorizationRule(
        category_id=rule.category_id,
        rule_type=rule.rule_type,
        pattern=rule.pattern,
        priority=rule.priority,
        is_active=True
    )
    
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    
    # Invalidate cache
    service = CategorizationService(db)
    service.invalidate_cache()
    
    return new_rule

@router.patch("/rules/{rule_id}")
async def update_rule(
    rule_id: int,
    updates: RuleUpdate,
    db: Session = Depends(get_db)
):
    """Update a categorization rule"""
    rule = db.query(CategorizationRule).filter(CategorizationRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Apply updates
    if updates.category_id is not None:
        category = db.query(Category).filter(Category.id == updates.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        rule.category_id = updates.category_id
    
    if updates.rule_type is not None:
        rule.rule_type = updates.rule_type
    
    if updates.pattern is not None:
        rule.pattern = updates.pattern
    
    if updates.priority is not None:
        rule.priority = updates.priority
    
    if updates.is_active is not None:
        rule.is_active = updates.is_active
    
    db.commit()
    db.refresh(rule)
    
    # Invalidate cache
    service = CategorizationService(db)
    service.invalidate_cache()
    
    return rule

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a categorization rule"""
    rule = db.query(CategorizationRule).filter(CategorizationRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    
    # Invalidate cache
    service = CategorizationService(db)
    service.invalidate_cache()
    
    return {"success": True, "message": "Rule deleted"}

@router.post("/categorize-all")
async def categorize_all(
    use_llm: bool = False,
    db: Session = Depends(get_db)
):
    """
    Run categorization on all uncategorized transactions
    
    Parameters:
    - use_llm: If true, use LLM for transactions that don't match any rules
    
    Process:
    1. Try rule-based categorization first (fast, free)
    2. If no rule matches and use_llm=true, use Claude API (slower, costs money)
    """
    service = CategorizationService(db)
    stats = service.categorize_all_uncategorized(use_llm_fallback=use_llm)
    
    return {
        "success": True,
        **stats
    }

@router.post("/transactions/{transaction_id}/categorize")
async def categorize_transaction(
    transaction_id: int,
    use_llm: bool = False,
    db: Session = Depends(get_db)
):
    """
    Categorize a single transaction
    
    Parameters:
    - use_llm: If true, use LLM fallback if no rule matches
    """
    from app.models import Transaction
    
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    service = CategorizationService(db)
    category_id, method, confidence = service.categorize_transaction(
        transaction,
        use_llm_fallback=use_llm
    )
    
    if category_id:
        transaction.category_id = category_id
        transaction.is_categorized = True
        transaction.categorization_method = method
        transaction.categorization_confidence = confidence
        db.commit()
        db.refresh(transaction)
        
        return {
            "success": True,
            "category_id": category_id,
            "method": method,
            "confidence": confidence,
            "transaction": transaction
        }
    else:
        return {
            "success": False,
            "message": "Could not categorize transaction (no matching rules and LLM disabled or failed)"
        }
