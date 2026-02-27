"""API routes for transaction import"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional
import tempfile
import os

from app.database import get_db
from app.services.import_service import ImportService, PARSER_REGISTRY

router = APIRouter()

@router.get("/supported-banks")
async def get_supported_banks(db: Session = Depends(get_db)):
    """Get list of supported bank formats"""
    service = ImportService(db)
    return {
        "banks": service.get_supported_banks()
    }

@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    account_id: int = Form(...),
    bank: Optional[str] = Form(None),
    skip_duplicates: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Upload and import a CSV file
    
    - **file**: CSV file from bank
    - **account_id**: Target account ID
    - **bank**: Bank name (optional, auto-detect if not provided)
    - **skip_duplicates**: Skip transactions that already exist
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = ImportService(db)
        
        # Find parser class if bank is specified
        parser_class = None
        if bank:
            for ParserClass in PARSER_REGISTRY:
                if ParserClass.bank_name.lower() == bank.lower():
                    parser_class = ParserClass
                    break
            
            if parser_class is None:
                raise HTTPException(status_code=400, detail=f"Unknown bank: {bank}")
        
        # Import transactions
        stats = service.import_transactions(
            file_path=tmp_path,
            account_id=account_id,
            parser_class=parser_class,
            skip_duplicates=skip_duplicates
        )
        
        return {
            "success": True,
            "filename": file.filename,
            **stats
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.post("/detect-format")
async def detect_format(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Detect the bank format of an uploaded CSV file without importing
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = ImportService(db)
        parser_class = service.detect_bank_format(tmp_path)
        
        if parser_class:
            return {
                "detected": True,
                "bank": parser_class.bank_name,
                "parser": parser_class.__name__
            }
        else:
            return {
                "detected": False,
                "message": "Could not detect bank format"
            }
    
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
