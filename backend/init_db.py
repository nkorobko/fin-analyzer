"""Initialize database and seed with default data"""
from app.database import init_db, SessionLocal
from app.seed_data import seed_categories

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✅ Database tables created")
    
    print("\nSeeding default categories...")
    db = SessionLocal()
    try:
        seed_categories(db)
    finally:
        db.close()
    
    print("\n🎉 Database initialization complete!")
