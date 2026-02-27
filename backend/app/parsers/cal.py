"""Cal credit card CSV parser"""
from typing import List
import pandas as pd
from .base import BaseParser, ParsedTransaction

class CalParser(BaseParser):
    """
    Parser for Cal (Israel Credit Cards) CSV exports
    """
    
    bank_name = "Cal"
    
    DATE_COLS = ['תאריך', 'Date', 'תאריך עסקה']
    MERCHANT_COLS = ['שם בית עסק', 'Merchant', 'בית עסק']
    AMOUNT_COLS = ['סכום', 'Amount']
    DESC_COLS = ['פירוט', 'Description']
    
    def can_parse(self, df: pd.DataFrame) -> bool:
        cols = [c.strip() for c in df.columns]
        has_date = any(col in cols for col in self.DATE_COLS)
        has_amount = any(col in cols for col in self.AMOUNT_COLS)
        return has_date and has_amount
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        cols = [c.strip() for c in df.columns]
        for name in possible_names:
            if name in cols:
                return name
        return None
    
    def parse(self, file_path: str) -> List[ParsedTransaction]:
        df = self.load_csv(file_path)
        
        if not self.can_parse(df):
            raise ValueError(f"File does not match {self.bank_name} format")
        
        date_col = self._find_column(df, self.DATE_COLS)
        merchant_col = self._find_column(df, self.MERCHANT_COLS)
        amount_col = self._find_column(df, self.AMOUNT_COLS)
        desc_col = self._find_column(df, self.DESC_COLS)
        
        transactions = []
        
        for idx, row in df.iterrows():
            if pd.isna(row[date_col]):
                continue
            
            date = self.parse_date(row[date_col])
            if not date:
                continue
            
            merchant = str(row[merchant_col]).strip() if merchant_col and not pd.isna(row[merchant_col]) else None
            description = str(row[desc_col]).strip() if desc_col and not pd.isna(row[desc_col]) else (merchant or "")
            
            amount = -abs(self.clean_amount(row[amount_col]))  # Credit card charges
            
            transaction = ParsedTransaction(
                date=date,
                amount=amount,
                description=description,
                merchant=merchant,
                raw_data=row.to_dict()
            )
            
            transactions.append(transaction)
        
        return transactions
