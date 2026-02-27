"""Transaction import service"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.models import Transaction, Account
from app.parsers import (
    BaseParser, LeumiParser, HapoalimParser, DiscountParser, MaxParser, CalParser
)

# Registry of available parsers
PARSER_REGISTRY = [
    LeumiParser,
    HapoalimParser,
    DiscountParser,
    MaxParser,
    CalParser,
]

class ImportService:
    """Service for importing transactions from CSV files"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_bank_format(self, file_path: str) -> Optional[BaseParser]:
        """
        Auto-detect which bank format the CSV file uses
        
        Returns the appropriate parser class or None if format is unknown
        """
        import pandas as pd
        
        # Try to read the file with each parser
        for ParserClass in PARSER_REGISTRY:
            try:
                # Create a temporary parser instance to test
                temp_parser = ParserClass(account_id=0, source_file=file_path)
                df = temp_parser.load_csv(file_path)
                
                if temp_parser.can_parse(df):
                    return ParserClass
            except Exception:
                continue
        
        return None
    
    def import_transactions(
        self,
        file_path: str,
        account_id: int,
        parser_class: Optional[type] = None,
        skip_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Import transactions from a CSV file
        
        Args:
            file_path: Path to the CSV file
            account_id: Target account ID
            parser_class: Specific parser to use (auto-detect if None)
            skip_duplicates: Skip transactions that already exist
        
        Returns:
            dict with import statistics
        """
        # Validate account exists
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Auto-detect format if not specified
        if parser_class is None:
            parser_class = self.detect_bank_format(file_path)
            if parser_class is None:
                raise ValueError("Could not detect bank format. Please specify parser manually.")
        
        # Create parser instance
        source_file = os.path.basename(file_path)
        parser = parser_class(account_id=account_id, source_file=source_file)
        
        # Parse transactions
        parsed_transactions = parser.parse(file_path)
        
        # Import statistics
        stats = {
            'total_parsed': len(parsed_transactions),
            'imported': 0,
            'skipped_duplicates': 0,
            'errors': 0,
            'bank': parser.bank_name,
        }
        
        for row_idx, parsed_tx in enumerate(parsed_transactions):
            try:
                # Check for duplicate
                if skip_duplicates and self._is_duplicate(account_id, parsed_tx):
                    stats['skipped_duplicates'] += 1
                    continue
                
                # Create transaction
                transaction = Transaction(
                    account_id=account_id,
                    date=parsed_tx.date,
                    amount=parsed_tx.amount,
                    description=parsed_tx.description,
                    merchant=parsed_tx.merchant,
                    original_currency=parsed_tx.original_currency,
                    original_amount=parsed_tx.original_amount,
                    source_file=source_file,
                    source_row=row_idx + 1,
                    is_categorized=False,
                )
                
                self.db.add(transaction)
                stats['imported'] += 1
            
            except Exception as e:
                stats['errors'] += 1
                print(f"Error importing transaction: {e}")
        
        # Commit all transactions
        self.db.commit()
        
        return stats
    
    def _is_duplicate(self, account_id: int, parsed_tx) -> bool:
        """
        Check if transaction already exists
        
        Matches on: account_id + date + amount + description
        """
        existing = self.db.query(Transaction).filter(
            Transaction.account_id == account_id,
            Transaction.date == parsed_tx.date,
            Transaction.amount == parsed_tx.amount,
            Transaction.description == parsed_tx.description,
        ).first()
        
        return existing is not None
    
    def get_supported_banks(self) -> List[Dict[str, str]]:
        """Get list of supported bank formats"""
        return [
            {'name': ParserClass.bank_name, 'class': ParserClass.__name__}
            for ParserClass in PARSER_REGISTRY
        ]
