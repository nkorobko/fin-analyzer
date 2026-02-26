"""Seed database with default Israeli categories"""
from sqlalchemy.orm import Session
from app.models import Category

DEFAULT_CATEGORIES = [
    # Income categories
    {"name": "Salary", "category_type": "income", "icon": "💼", "is_system": True},
    {"name": "Freelance", "category_type": "income", "icon": "💻", "is_system": True},
    {"name": "Investment Returns", "category_type": "income", "icon": "📈", "is_system": True},
    {"name": "Other Income", "category_type": "income", "icon": "💰", "is_system": True},
    
    # Expense categories
    {"name": "Groceries", "category_type": "expense", "icon": "🛒", "color": "#10B981", "is_system": True},
    {"name": "Dining Out", "category_type": "expense", "icon": "🍽️", "color": "#F59E0B", "is_system": True},
    {"name": "Transportation", "category_type": "expense", "icon": "🚗", "color": "#3B82F6", "is_system": True},
    {"name": "Utilities", "category_type": "expense", "icon": "💡", "color": "#8B5CF6", "is_system": True},
    {"name": "Housing", "category_type": "expense", "icon": "🏠", "color": "#EF4444", "is_system": True},
    {"name": "Healthcare", "category_type": "expense", "icon": "⚕️", "color": "#EC4899", "is_system": True},
    {"name": "Entertainment", "category_type": "expense", "icon": "🎬", "color": "#06B6D4", "is_system": True},
    {"name": "Shopping", "category_type": "expense", "icon": "🛍️", "color": "#F97316", "is_system": True},
    {"name": "Education", "category_type": "expense", "icon": "📚", "color": "#14B8A6", "is_system": True},
    {"name": "Insurance", "category_type": "expense", "icon": "🛡️", "color": "#6366F1", "is_system": True},
    {"name": "Subscriptions", "category_type": "expense", "icon": "📱", "color": "#A855F7", "is_system": True},
    {"name": "Personal Care", "category_type": "expense", "icon": "💅", "color": "#EC4899", "is_system": True},
    {"name": "Gifts & Donations", "category_type": "expense", "icon": "🎁", "color": "#F43F5E", "is_system": True},
    {"name": "Travel", "category_type": "expense", "icon": "✈️", "color": "#0EA5E9", "is_system": True},
    {"name": "Fitness", "category_type": "expense", "icon": "💪", "color": "#22C55E", "is_system": True},
    {"name": "Other Expenses", "category_type": "expense", "icon": "📦", "color": "#64748B", "is_system": True},
]

# Subcategories (linked to parent categories by name)
DEFAULT_SUBCATEGORIES = [
    # Transportation subcategories
    {"name": "Gas", "parent_name": "Transportation", "category_type": "expense", "icon": "⛽"},
    {"name": "Public Transit", "parent_name": "Transportation", "category_type": "expense", "icon": "🚌"},
    {"name": "Parking", "parent_name": "Transportation", "category_type": "expense", "icon": "🅿️"},
    {"name": "Car Maintenance", "parent_name": "Transportation", "category_type": "expense", "icon": "🔧"},
    
    # Utilities subcategories
    {"name": "Electricity", "parent_name": "Utilities", "category_type": "expense", "icon": "⚡"},
    {"name": "Water", "parent_name": "Utilities", "category_type": "expense", "icon": "💧"},
    {"name": "Internet", "parent_name": "Utilities", "category_type": "expense", "icon": "🌐"},
    {"name": "Phone", "parent_name": "Utilities", "category_type": "expense", "icon": "📞"},
]

def seed_categories(db: Session):
    """Seed default categories if they don't exist"""
    existing_count = db.query(Category).count()
    
    if existing_count > 0:
        print(f"Categories already exist ({existing_count} found). Skipping seed.")
        return
    
    # First, create all parent categories
    category_map = {}
    for cat_data in DEFAULT_CATEGORIES:
        category = Category(**cat_data)
        db.add(category)
        db.flush()  # Get the ID
        category_map[cat_data["name"]] = category.id
    
    # Then create subcategories
    for subcat_data in DEFAULT_SUBCATEGORIES:
        parent_name = subcat_data.pop("parent_name")
        parent_id = category_map.get(parent_name)
        if parent_id:
            subcat_data["parent_id"] = parent_id
            subcategory = Category(**subcat_data)
            db.add(subcategory)
    
    db.commit()
    print(f"✅ Seeded {len(DEFAULT_CATEGORIES)} categories and {len(DEFAULT_SUBCATEGORIES)} subcategories")
