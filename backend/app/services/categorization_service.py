"""Transaction categorization service"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
import re
import anthropic
import json

from app.models import Transaction, Category, CategorizationRule
from app.config import settings

class CategorizationService:
    """Service for automatically categorizing transactions"""
    
    def __init__(self, db: Session):
        self.db = db
        self._rules_cache = None
    
    def categorize_transaction(
        self,
        transaction: Transaction,
        use_llm_fallback: bool = False
    ) -> Tuple[Optional[int], str, float]:
        """
        Categorize a single transaction
        
        Returns:
            Tuple of (category_id, method, confidence)
            - category_id: The assigned category ID (or None)
            - method: 'rule' or 'llm'
            - confidence: 0.0-1.0 confidence score
        """
        # Try rule-based categorization first
        category_id = self._categorize_by_rules(transaction)
        
        if category_id:
            return category_id, 'rule', 1.0
        
        # LLM fallback for unmatched transactions
        if use_llm_fallback:
            category_id, confidence = self._categorize_by_llm(transaction)
            if category_id:
                return category_id, 'llm', confidence
        
        return None, 'none', 0.0
    
    def _categorize_by_rules(self, transaction: Transaction) -> Optional[int]:
        """
        Apply rule-based categorization
        
        Rules are evaluated in priority order (highest first)
        First matching rule wins
        """
        # Load and cache rules
        if self._rules_cache is None:
            self._rules_cache = self._load_rules()
        
        # Prepare text to match against
        text = transaction.description.lower()
        merchant = (transaction.merchant or '').lower()
        
        # Try each rule in priority order
        for rule in self._rules_cache:
            if self._rule_matches(rule, text, merchant):
                return rule.category_id
        
        return None
    
    def _load_rules(self) -> List[CategorizationRule]:
        """Load active rules sorted by priority (highest first)"""
        return self.db.query(CategorizationRule)\
            .filter(CategorizationRule.is_active == True)\
            .order_by(CategorizationRule.priority.desc())\
            .all()
    
    def _rule_matches(
        self,
        rule: CategorizationRule,
        description: str,
        merchant: str
    ) -> bool:
        """Check if a rule matches the transaction"""
        pattern = rule.pattern.lower()
        
        if rule.rule_type == 'keyword':
            # Simple substring match
            return pattern in description or pattern in merchant
        
        elif rule.rule_type == 'regex':
            # Regex match
            try:
                regex = re.compile(pattern, re.IGNORECASE)
                return bool(regex.search(description)) or bool(regex.search(merchant))
            except re.error:
                # Invalid regex, skip
                return False
        
        elif rule.rule_type == 'merchant':
            # Exact merchant match
            return pattern == merchant
        
        return False
    
    def categorize_all_uncategorized(self, use_llm_fallback: bool = False) -> dict:
        """
        Categorize all uncategorized transactions
        
        Returns statistics about the categorization run
        """
        uncategorized = self.db.query(Transaction)\
            .filter(Transaction.is_categorized == False)\
            .all()
        
        stats = {
            'total': len(uncategorized),
            'categorized': 0,
            'failed': 0,
            'by_rule': 0,
            'by_llm': 0,
        }
        
        for transaction in uncategorized:
            category_id, method, confidence = self.categorize_transaction(
                transaction,
                use_llm_fallback=use_llm_fallback
            )
            
            if category_id:
                transaction.category_id = category_id
                transaction.is_categorized = True
                transaction.categorization_method = method
                transaction.categorization_confidence = confidence
                stats['categorized'] += 1
                
                if method == 'rule':
                    stats['by_rule'] += 1
                elif method == 'llm':
                    stats['by_llm'] += 1
            else:
                stats['failed'] += 1
        
        self.db.commit()
        
        return stats
    
    def invalidate_cache(self):
        """Invalidate the rules cache (call after adding/updating rules)"""
        self._rules_cache = None
    
    def _categorize_by_llm(self, transaction: Transaction) -> Tuple[Optional[int], float]:
        """
        Use Claude API to categorize transaction
        
        Returns:
            Tuple of (category_id, confidence)
        """
        if not settings.ANTHROPIC_API_KEY:
            return None, 0.0
        
        try:
            # Get all available categories
            categories = self.db.query(Category).filter(Category.category_type == 'expense').all()
            
            if not categories:
                return None, 0.0
            
            # Build category list for prompt
            category_list = "\n".join([
                f"- {cat.name} ({cat.id})"
                for cat in categories
            ])
            
            # Determine if income or expense
            amount_type = "income" if transaction.amount > 0 else "expense"
            
            # Build prompt
            prompt = f"""Analyze this financial transaction and categorize it.

Transaction Details:
- Description: {transaction.description}
- Merchant: {transaction.merchant or 'N/A'}
- Amount: {abs(transaction.amount)} ILS ({amount_type})
- Date: {transaction.date.strftime('%Y-%m-%d')}

Available Categories (ID - Name):
{category_list}

Instructions:
1. Choose the MOST appropriate category from the list above
2. Consider that this is an Israeli transaction (may contain Hebrew text)
3. Common Israeli merchants: שופרסל (groceries), פז (gas), ארומה (coffee), etc.
4. Respond ONLY with valid JSON in this exact format:
{{"category_id": <number>, "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}}

Your response:"""

            # Call Claude API
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            response_text = message.content[0].text.strip()
            
            # Extract JSON (Claude sometimes wraps it in markdown)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response_text)
            
            category_id = result.get('category_id')
            confidence = result.get('confidence', 0.5)
            
            # Validate category exists
            if category_id:
                category = self.db.query(Category).filter(Category.id == category_id).first()
                if category:
                    return category_id, confidence
            
            return None, 0.0
        
        except Exception as e:
            print(f"LLM categorization error: {e}")
            return None, 0.0


def create_default_rules(db: Session):
    """Create default Israeli categorization rules"""
    
    # Check if rules already exist
    existing = db.query(CategorizationRule).count()
    if existing > 0:
        print(f"Rules already exist ({existing} found). Skipping.")
        return
    
    # Get category IDs by name
    def get_category_id(name: str) -> Optional[int]:
        cat = db.query(Category).filter(Category.name == name).first()
        return cat.id if cat else None
    
    # Default rules for Israeli merchants
    default_rules = [
        # Groceries
        {'pattern': 'שופרסל', 'type': 'keyword', 'category': 'Groceries', 'priority': 100},
        {'pattern': 'רמי לוי', 'type': 'keyword', 'category': 'Groceries', 'priority': 100},
        {'pattern': 'יינות ביתן', 'type': 'keyword', 'category': 'Groceries', 'priority': 100},
        {'pattern': 'ויקטורי', 'type': 'keyword', 'category': 'Groceries', 'priority': 100},
        {'pattern': 'סופר', 'type': 'keyword', 'category': 'Groceries', 'priority': 80},
        {'pattern': 'מכולת', 'type': 'keyword', 'category': 'Groceries', 'priority': 80},
        
        # Gas stations
        {'pattern': 'פז', 'type': 'keyword', 'category': 'Gas', 'priority': 100},
        {'pattern': 'סונול', 'type': 'keyword', 'category': 'Gas', 'priority': 100},
        {'pattern': 'דלק', 'type': 'keyword', 'category': 'Gas', 'priority': 100},
        {'pattern': 'דור אלון', 'type': 'keyword', 'category': 'Gas', 'priority': 100},
        {'pattern': 'תדלוק', 'type': 'keyword', 'category': 'Gas', 'priority': 90},
        
        # Dining
        {'pattern': 'מסעדה', 'type': 'keyword', 'category': 'Dining Out', 'priority': 90},
        {'pattern': 'קפה', 'type': 'keyword', 'category': 'Dining Out', 'priority': 80},
        {'pattern': 'ארומה', 'type': 'keyword', 'category': 'Dining Out', 'priority': 100},
        {'pattern': 'קפה גרג', 'type': 'keyword', 'category': 'Dining Out', 'priority': 100},
        {'pattern': 'מקדונלד', 'type': 'keyword', 'category': 'Dining Out', 'priority': 100},
        {'pattern': 'בורגר', 'type': 'keyword', 'category': 'Dining Out', 'priority': 80},
        
        # Pharmacies
        {'pattern': 'סופר פארם', 'type': 'keyword', 'category': 'Healthcare', 'priority': 100},
        {'pattern': 'ניו פארם', 'type': 'keyword', 'category': 'Healthcare', 'priority': 100},
        {'pattern': 'בית מרקחת', 'type': 'keyword', 'category': 'Healthcare', 'priority': 90},
        
        # Public transit
        {'pattern': 'רב קו', 'type': 'keyword', 'category': 'Public Transit', 'priority': 100},
        {'pattern': 'אגד', 'type': 'keyword', 'category': 'Public Transit', 'priority': 100},
        {'pattern': 'דן', 'type': 'keyword', 'category': 'Public Transit', 'priority': 90},
        
        # Online services
        {'pattern': 'נטפליקס', 'type': 'keyword', 'category': 'Subscriptions', 'priority': 100},
        {'pattern': 'netflix', 'type': 'keyword', 'category': 'Subscriptions', 'priority': 100},
        {'pattern': 'spotify', 'type': 'keyword', 'category': 'Subscriptions', 'priority': 100},
        {'pattern': 'amazon', 'type': 'keyword', 'category': 'Shopping', 'priority': 90},
        {'pattern': 'amzn', 'type': 'keyword', 'category': 'Shopping', 'priority': 90},
        
        # Utilities
        {'pattern': 'חברת חשמל', 'type': 'keyword', 'category': 'Electricity', 'priority': 100},
        {'pattern': 'חח"י', 'type': 'keyword', 'category': 'Electricity', 'priority': 100},
        {'pattern': 'מקורות', 'type': 'keyword', 'category': 'Water', 'priority': 100},
        {'pattern': 'בזק', 'type': 'keyword', 'category': 'Internet', 'priority': 100},
        {'pattern': 'סלקום', 'type': 'keyword', 'category': 'Phone', 'priority': 100},
        {'pattern': 'פרטנר', 'type': 'keyword', 'category': 'Phone', 'priority': 100},
        
        # Parking
        {'pattern': 'חניה', 'type': 'keyword', 'category': 'Parking', 'priority': 100},
        {'pattern': 'פאנגו', 'type': 'keyword', 'category': 'Parking', 'priority': 100},
        
        # Salary (income)
        {'pattern': 'משכורת', 'type': 'keyword', 'category': 'Salary', 'priority': 100},
        {'pattern': 'העברה - משכורת', 'type': 'keyword', 'category': 'Salary', 'priority': 100},
    ]
    
    rules_created = 0
    
    for rule_data in default_rules:
        category_id = get_category_id(rule_data['category'])
        
        if not category_id:
            print(f"Warning: Category '{rule_data['category']}' not found, skipping rule")
            continue
        
        rule = CategorizationRule(
            category_id=category_id,
            rule_type=rule_data['type'],
            pattern=rule_data['pattern'],
            priority=rule_data['priority'],
            is_active=True
        )
        
        db.add(rule)
        rules_created += 1
    
    db.commit()
    print(f"✅ Created {rules_created} default categorization rules")
