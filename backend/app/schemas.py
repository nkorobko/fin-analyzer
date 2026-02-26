from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Account schemas
class AccountBase(BaseModel):
    name: str
    bank_name: str
    account_number: Optional[str] = None
    account_type: str
    currency: str = "ILS"
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    category_type: str
    icon: Optional[str] = None
    color: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    is_system: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Transaction schemas
class TransactionBase(BaseModel):
    account_id: int
    date: datetime
    amount: float
    description: str
    merchant: Optional[str] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    is_categorized: bool
    categorization_method: Optional[str]
    categorization_confidence: Optional[float]
    is_recurring: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Budget schemas
class BudgetBase(BaseModel):
    category_id: int
    amount: float
    period: str = "monthly"
    start_date: datetime
    end_date: Optional[datetime] = None
    alert_threshold: float = 0.8

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Savings goal schemas
class SavingsGoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[datetime] = None
    description: Optional[str] = None

class SavingsGoalCreate(SavingsGoalBase):
    pass

class SavingsGoal(SavingsGoalBase):
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
