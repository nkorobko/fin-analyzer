from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title="Fin Analyzer API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Fin Analyzer API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Future routes will be added here
# from app.routes import transactions, categories, budgets
# app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
# app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
# app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])
