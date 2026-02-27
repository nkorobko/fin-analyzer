"""Discount Bank CSV parser"""
from typing import List
import pandas as pd
from .base import BaseParser, ParsedTransaction

class DiscountParser(BaseParser):
    """
    Parser for Discount Bank CSV exports
    """
    
    bank_name = "Discount"
    
    DATE_COLS = ['תאריך', 'Date', 'תאריך ערך']
    DESC_COLS = ['תיאור', 'Description', 'הערות']
    DEBIT_COLS = ['חובה', 'Debit']
    CREDIT_COLS = ['זכות', 'Credit']
    
    def can_parse(self, df: pd.DataFrame) -> bool:
        cols = [c.strip() for c in df.columns]
        has_date = any(col in cols for col in self.DATE_COLS)
        has_desc = any(col in cols for col in self.DESC_COLS)
        return has_date and has_desc
    
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
        desc_col = self._find_column(df, self.DESC_COLS)
        debit_col = self._find_column(df, self.DEBIT_COLS)
        credit_col = self._find_column(df, self.CREDIT_COLS)
        
        transactions = []
        
        for idx, row in df.iterrows():
            if pd.isna(row[date_col]):
                continue
            
            date = self.parse_date(row[date_col])
            if not date:
                continue
            
            description = str(row[desc_col]).strip() if not pd.isna(row[desc_col]) else ""
            
            debit = self.clean_amount(row[debit_col]) if debit_col else 0.0
            credit = self.clean_amount(row[credit_col]) if credit_col else 0.0
            amount = credit - debit
            
            transaction = ParsedTransaction(
                date=date,
                amount=amount,
                description=description,
                raw_data=row.to_dict()
            )
            
            transactions.append(transaction)
        
        return transactions
