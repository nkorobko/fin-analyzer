"""Leumi Bank CSV parser"""
from typing import List
import pandas as pd
from .base import BaseParser, ParsedTransaction

class LeumiParser(BaseParser):
    """
    Parser for Bank Leumi CSV exports
    
    Expected columns (Hebrew):
    - תאריך (Date)
    - תיאור (Description)
    - אסמכתא (Reference)
    - חובה (Debit)
    - זכות (Credit)
    - יתרה (Balance)
    """
    
    bank_name = "Leumi"
    
    # Column name variations
    DATE_COLS = ['תאריך', 'Date', 'תאריך עסקה']
    DESC_COLS = ['תיאור', 'Description', 'פירוט']
    DEBIT_COLS = ['חובה', 'Debit', 'חיוב']
    CREDIT_COLS = ['זכות', 'Credit', 'זיכוי']
    REF_COLS = ['אסמכתא', 'Reference', 'מספר אסמכתא']
    
    def can_parse(self, df: pd.DataFrame) -> bool:
        """Check if CSV matches Leumi format"""
        cols = [c.strip() for c in df.columns]
        
        # Check for key Leumi columns
        has_date = any(col in cols for col in self.DATE_COLS)
        has_desc = any(col in cols for col in self.DESC_COLS)
        has_debit = any(col in cols for col in self.DEBIT_COLS)
        has_credit = any(col in cols for col in self.CREDIT_COLS)
        
        return has_date and has_desc and (has_debit or has_credit)
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> str:
        """Find column by possible names"""
        cols = [c.strip() for c in df.columns]
        for name in possible_names:
            if name in cols:
                return name
        return None
    
    def parse(self, file_path: str) -> List[ParsedTransaction]:
        """Parse Leumi CSV file"""
        df = self.load_csv(file_path)
        
        if not self.can_parse(df):
            raise ValueError(f"File does not match {self.bank_name} format")
        
        # Find column names
        date_col = self._find_column(df, self.DATE_COLS)
        desc_col = self._find_column(df, self.DESC_COLS)
        debit_col = self._find_column(df, self.DEBIT_COLS)
        credit_col = self._find_column(df, self.CREDIT_COLS)
        ref_col = self._find_column(df, self.REF_COLS)
        
        transactions = []
        
        for idx, row in df.iterrows():
            # Skip rows with no date
            if pd.isna(row[date_col]):
                continue
            
            date = self.parse_date(row[date_col])
            if not date:
                continue
            
            description = str(row[desc_col]).strip() if not pd.isna(row[desc_col]) else ""
            
            # Calculate amount (credit is positive, debit is negative)
            debit = self.clean_amount(row[debit_col]) if debit_col else 0.0
            credit = self.clean_amount(row[credit_col]) if credit_col else 0.0
            amount = credit - debit  # Net amount
            
            reference = str(row[ref_col]).strip() if ref_col and not pd.isna(row[ref_col]) else None
            
            transaction = ParsedTransaction(
                date=date,
                amount=amount,
                description=description,
                reference=reference,
                raw_data=row.to_dict()
            )
            
            transactions.append(transaction)
        
        return transactions
