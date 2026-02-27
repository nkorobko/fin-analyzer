"""Bank Hapoalim CSV parser"""
from typing import List
import pandas as pd
from .base import BaseParser, ParsedTransaction

class HapoalimParser(BaseParser):
    """
    Parser for Bank Hapoalim CSV exports
    
    Expected columns (Hebrew):
    - תאריך (Date)
    - תיאור (Description)
    - סכום חיוב (Debit Amount)
    - סכום זיכוי (Credit Amount)
    - יתרה (Balance)
    """
    
    bank_name = "Hapoalim"
    
    DATE_COLS = ['תאריך', 'Date', 'תאריך ביצוע']
    DESC_COLS = ['תיאור', 'Description', 'פירוט התנועה']
    DEBIT_COLS = ['סכום חיוב', 'Debit', 'חובה']
    CREDIT_COLS = ['סכום זיכוי', 'Credit', 'זכות']
    MERCHANT_COLS = ['שם בית עסק', 'Merchant']
    
    def can_parse(self, df: pd.DataFrame) -> bool:
        """Check if CSV matches Hapoalim format"""
        cols = [c.strip() for c in df.columns]
        
        has_date = any(col in cols for col in self.DATE_COLS)
        has_desc = any(col in cols for col in self.DESC_COLS)
        has_amount = any(col in cols for col in self.DEBIT_COLS + self.CREDIT_COLS)
        
        return has_date and has_desc and has_amount
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        cols = [c.strip() for c in df.columns]
        for name in possible_names:
            if name in cols:
                return name
        return None
    
    def parse(self, file_path: str) -> List[ParsedTransaction]:
        """Parse Hapoalim CSV file"""
        df = self.load_csv(file_path)
        
        if not self.can_parse(df):
            raise ValueError(f"File does not match {self.bank_name} format")
        
        date_col = self._find_column(df, self.DATE_COLS)
        desc_col = self._find_column(df, self.DESC_COLS)
        debit_col = self._find_column(df, self.DEBIT_COLS)
        credit_col = self._find_column(df, self.CREDIT_COLS)
        merchant_col = self._find_column(df, self.MERCHANT_COLS)
        
        transactions = []
        
        for idx, row in df.iterrows():
            if pd.isna(row[date_col]):
                continue
            
            date = self.parse_date(row[date_col])
            if not date:
                continue
            
            description = str(row[desc_col]).strip() if not pd.isna(row[desc_col]) else ""
            merchant = str(row[merchant_col]).strip() if merchant_col and not pd.isna(row[merchant_col]) else None
            
            debit = self.clean_amount(row[debit_col]) if debit_col else 0.0
            credit = self.clean_amount(row[credit_col]) if credit_col else 0.0
            amount = credit - debit
            
            transaction = ParsedTransaction(
                date=date,
                amount=amount,
                description=description,
                merchant=merchant,
                raw_data=row.to_dict()
            )
            
            transactions.append(transaction)
        
        return transactions
