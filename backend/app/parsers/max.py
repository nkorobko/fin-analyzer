"""Max credit card CSV parser"""
from typing import List
import pandas as pd
from .base import BaseParser, ParsedTransaction

class MaxParser(BaseParser):
    """
    Parser for Max (Leumi Card) credit card CSV exports
    
    Credit card format typically shows:
    - Purchase date
    - Merchant name
    - Amount (all negative for purchases)
    - Payment date
    """
    
    bank_name = "Max"
    
    DATE_COLS = ['תאריך רכישה', 'Purchase Date', 'תאריך']
    MERCHANT_COLS = ['שם בית עסק', 'Merchant', 'בית עסק']
    AMOUNT_COLS = ['סכום', 'Amount', 'סכום עסקה']
    PAYMENT_DATE_COLS = ['תאריך חיוב', 'Payment Date']
    CURRENCY_COLS = ['מטבע', 'Currency']
    ORIGINAL_AMOUNT_COLS = ['סכום מקורי', 'Original Amount']
    
    def can_parse(self, df: pd.DataFrame) -> bool:
        cols = [c.strip() for c in df.columns]
        has_date = any(col in cols for col in self.DATE_COLS)
        has_merchant = any(col in cols for col in self.MERCHANT_COLS)
        has_amount = any(col in cols for col in self.AMOUNT_COLS)
        return has_date and has_merchant and has_amount
    
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
        currency_col = self._find_column(df, self.CURRENCY_COLS)
        original_amount_col = self._find_column(df, self.ORIGINAL_AMOUNT_COLS)
        
        transactions = []
        
        for idx, row in df.iterrows():
            if pd.isna(row[date_col]):
                continue
            
            date = self.parse_date(row[date_col])
            if not date:
                continue
            
            merchant = str(row[merchant_col]).strip() if not pd.isna(row[merchant_col]) else ""
            amount = -abs(self.clean_amount(row[amount_col]))  # Credit card charges are negative
            
            # Handle foreign currency transactions
            original_currency = None
            original_amount = None
            if currency_col and not pd.isna(row[currency_col]):
                currency = str(row[currency_col]).strip()
                if currency != 'ILS':
                    original_currency = currency
                    original_amount = self.clean_amount(row[original_amount_col]) if original_amount_col else amount
            
            transaction = ParsedTransaction(
                date=date,
                amount=amount,
                description=merchant,
                merchant=merchant,
                original_currency=original_currency,
                original_amount=original_amount,
                raw_data=row.to_dict()
            )
            
            transactions.append(transaction)
        
        return transactions
