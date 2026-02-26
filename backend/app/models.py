from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Leumi Checking"
    bank_name = Column(String, nullable=False)  # e.g., "Leumi", "Max"
    account_number = Column(String, nullable=True)  # Last 4 digits or masked
    account_type = Column(String, nullable=False)  # checking, savings, credit_card
    currency = Column(String, default="ILS")  # ILS, USD, EUR
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account {self.bank_name} - {self.name}>"


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # For subcategories
    category_type = Column(String, nullable=False)  # income, expense
    icon = Column(String, nullable=True)  # emoji or icon name
    color = Column(String, nullable=True)  # hex color code
    is_system = Column(Boolean, default=False)  # System categories can't be deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    rules = relationship("CategorizationRule", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    amount = Column(Float, nullable=False)  # Positive for income, negative for expense
    description = Column(String, nullable=False)
    merchant = Column(String, nullable=True)  # Extracted/cleaned merchant name
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    
    # Categorization metadata
    is_categorized = Column(Boolean, default=False)
    categorization_method = Column(String, nullable=True)  # manual, rule, llm
    categorization_confidence = Column(Float, nullable=True)  # 0-1 for LLM predictions
    
    # Additional fields
    original_currency = Column(String, nullable=True)
    original_amount = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurring_group_id = Column(String, nullable=True)  # Groups recurring transactions
    
    # Source tracking
    source_file = Column(String, nullable=True)  # Original CSV filename
    source_row = Column(Integer, nullable=True)  # Row number in source file
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_date_amount', 'date', 'amount'),
        Index('idx_account_date', 'account_id', 'date'),
        Index('idx_category_date', 'category_id', 'date'),
    )
    
    def __repr__(self):
        return f"<Transaction {self.date.date()} {self.amount} {self.description[:30]}>"


class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)  # Monthly budget limit
    period = Column(String, default="monthly")  # monthly, yearly, weekly
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # Null = ongoing
    alert_threshold = Column(Float, default=0.8)  # Alert at 80% by default
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="budgets")
    
    def __repr__(self):
        return f"<Budget {self.category.name if self.category else 'Unknown'}: {self.amount}>"


class SavingsGoal(Base):
    __tablename__ = "savings_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SavingsGoal {self.name}: {self.current_amount}/{self.target_amount}>"


class CategorizationRule(Base):
    __tablename__ = "categorization_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    rule_type = Column(String, nullable=False)  # keyword, regex, merchant
    pattern = Column(String, nullable=False)  # The pattern to match
    priority = Column(Integer, default=0)  # Higher priority rules execute first
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="rules")
    
    # Index for fast rule matching
    __table_args__ = (
        Index('idx_rule_active', 'is_active', 'priority'),
    )
    
    def __repr__(self):
        return f"<Rule {self.rule_type}: {self.pattern} -> {self.category.name if self.category else 'Unknown'}>"
