"""API routes for categories"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Category
from app.schemas import Category as CategorySchema, CategoryCreate

router = APIRouter()

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None

@router.get("/", response_model=List[CategorySchema])
async def get_categories(
    category_type: Optional[str] = None,
    include_subcategories: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all categories
    
    Parameters:
    - category_type: Filter by 'income' or 'expense'
    - include_subcategories: Include child categories
    """
    query = db.query(Category)
    
    if category_type:
        query = query.filter(Category.category_type == category_type)
    
    if not include_subcategories:
        query = query.filter(Category.parent_id == None)
    
    categories = query.order_by(Category.name).all()
    return categories

@router.get("/tree")
async def get_category_tree(db: Session = Depends(get_db)):
    """
    Get categories as a hierarchical tree structure
    
    Returns parent categories with their subcategories nested
    """
    # Get all parent categories
    parents = db.query(Category).filter(Category.parent_id == None).order_by(Category.name).all()
    
    tree = []
    for parent in parents:
        parent_dict = {
            "id": parent.id,
            "name": parent.name,
            "category_type": parent.category_type,
            "icon": parent.icon,
            "color": parent.color,
            "is_system": parent.is_system,
            "subcategories": []
        }
        
        # Get subcategories
        subcats = db.query(Category).filter(Category.parent_id == parent.id).order_by(Category.name).all()
        for subcat in subcats:
            parent_dict["subcategories"].append({
                "id": subcat.id,
                "name": subcat.name,
                "category_type": subcat.category_type,
                "icon": subcat.icon,
                "color": subcat.color,
                "is_system": subcat.is_system,
            })
        
        tree.append(parent_dict)
    
    return tree

@router.get("/{category_id}", response_model=CategorySchema)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a single category by ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category

@router.post("/", response_model=CategorySchema)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    # Check if name already exists
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    # Validate parent exists if specified
    if category.parent_id:
        parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    new_category = Category(
        name=category.name,
        parent_id=category.parent_id,
        category_type=category.category_type,
        icon=category.icon,
        color=category.color,
        is_system=False
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category

@router.patch("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    updates: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Prevent modifying system categories' core properties
    if category.is_system and updates.name:
        raise HTTPException(status_code=400, detail="Cannot rename system categories")
    
    # Apply updates
    if updates.name:
        # Check name uniqueness
        existing = db.query(Category).filter(
            Category.name == updates.name,
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
        category.name = updates.name
    
    if updates.parent_id is not None:
        if updates.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")
        
        if updates.parent_id > 0:
            parent = db.query(Category).filter(Category.id == updates.parent_id).first()
            if not parent:
                raise HTTPException(status_code=400, detail="Parent category not found")
        
        category.parent_id = updates.parent_id if updates.parent_id > 0 else None
    
    if updates.icon is not None:
        category.icon = updates.icon
    
    if updates.color is not None:
        category.color = updates.color
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system categories")
    
    # Check if category has transactions
    from app.models import Transaction
    transaction_count = db.query(Transaction).filter(Transaction.category_id == category_id).count()
    
    if transaction_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {transaction_count} transactions. Re-categorize them first."
        )
    
    # Check if category has subcategories
    subcat_count = db.query(Category).filter(Category.parent_id == category_id).count()
    
    if subcat_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {subcat_count} subcategories. Delete or move them first."
        )
    
    db.delete(category)
    db.commit()
    
    return {"success": True, "message": "Category deleted"}

@router.post("/{category_id}/merge")
async def merge_categories(
    category_id: int,
    target_category_id: int,
    db: Session = Depends(get_db)
):
    """
    Merge this category into another category
    
    Moves all transactions and rules to the target category, then deletes this one
    """
    source = db.query(Category).filter(Category.id == category_id).first()
    target = db.query(Category).filter(Category.id == target_category_id).first()
    
    if not source or not target:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if source.is_system:
        raise HTTPException(status_code=400, detail="Cannot merge system categories")
    
    # Move transactions
    from app.models import Transaction, CategorizationRule
    
    transactions = db.query(Transaction).filter(Transaction.category_id == category_id).all()
    for tx in transactions:
        tx.category_id = target_category_id
    
    # Move rules
    rules = db.query(CategorizationRule).filter(CategorizationRule.category_id == category_id).all()
    for rule in rules:
        rule.category_id = target_category_id
    
    # Delete source category
    db.delete(source)
    db.commit()
    
    return {
        "success": True,
        "message": f"Merged {len(transactions)} transactions and {len(rules)} rules into target category"
    }
