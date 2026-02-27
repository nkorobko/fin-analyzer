"""Base parser interface for bank CSV files"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import chardet

class ParsedTransaction:
    """Standardized transaction format"""
    def __init__(
        self,
        date: datetime,
        amount: float,
        description: str,
        merchant: Optional[str] = None,
        original_currency: Optional[str] = None,
        original_amount: Optional[float] = None,
        reference: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.date = date
        self.amount = amount
        self.description = description
        self.merchant = merchant
        self.original_currency = original_currency
        self.original_amount = original_amount
        self.reference = reference
        self.raw_data = raw_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date,
            'amount': self.amount,
            'description': self.description,
            'merchant': self.merchant,
            'original_currency': self.original_currency,
            'original_amount': self.original_amount,
            'reference': self.reference,
            'raw_data': self.raw_data,
        }


class BaseParser(ABC):
    """Base class for bank-specific CSV parsers"""
    
    bank_name: str = "Unknown"
    supported_encodings = ['utf-8', 'windows-1255', 'iso-8859-8']
    
    def __init__(self, account_id: int, source_file: str):
        self.account_id = account_id
        self.source_file = source_file
    
    def detect_encoding(self, file_content: bytes) -> str:
        """Detect file encoding"""
        result = chardet.detect(file_content)
        detected = result.get('encoding', 'utf-8')
        
        # Fallback to common Israeli encodings
        if detected not in self.supported_encodings:
            for enc in self.supported_encodings:
                try:
                    file_content.decode(enc)
                    return enc
                except:
                    continue
        
        return detected or 'utf-8'
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV with automatic encoding detection"""
        with open(file_path, 'rb') as f:
            content = f.read()
        
        encoding = self.detect_encoding(content)
        
        # Try reading with detected encoding
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return df
        except Exception as e:
            # Fallback: try each supported encoding
            for enc in self.supported_encodings:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    return df
                except:
                    continue
            
            raise ValueError(f"Could not parse CSV with any supported encoding: {e}")
    
    @abstractmethod
    def can_parse(self, df: pd.DataFrame) -> bool:
        """Check if this parser can handle the given CSV format"""
        pass
    
    @abstractmethod
    def parse(self, file_path: str) -> List[ParsedTransaction]:
        """Parse CSV file and return list of standardized transactions"""
        pass
    
    def clean_amount(self, amount_str: str) -> float:
        """Clean and parse amount string (handles Hebrew formatting)"""
        if pd.isna(amount_str):
            return 0.0
        
        # Remove common Israeli formatting
        cleaned = str(amount_str).replace('₪', '').replace(',', '').replace(' ', '').strip()
        
        # Handle parentheses for negative numbers
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str, formats: List[str] = None) -> Optional[datetime]:
        """Parse date with multiple format support"""
        if pd.isna(date_str):
            return None
        
        default_formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d/%m/%y',
        ]
        
        formats = formats or default_formats
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        return None
