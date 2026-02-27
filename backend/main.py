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

# Import routes
from app.routes import import_routes, transaction_routes
app.include_router(import_routes.router, prefix="/api/import", tags=["import"])
app.include_router(transaction_routes.router, prefix="/api/transactions", tags=["transactions"])
