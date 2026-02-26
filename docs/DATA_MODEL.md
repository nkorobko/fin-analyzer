# Data Model Documentation

## Overview

The Fin Analyzer data model is designed for personal finance tracking with AI-powered categorization, budgeting, and analytics.

## Core Tables

### Accounts
Represents bank accounts and credit cards.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String | User-friendly name (e.g., "Leumi Checking") |
| bank_name | String | Bank/institution name |
| account_number | String | Last 4 digits or masked number |
| account_type | String | `checking`, `savings`, `credit_card` |
| currency | String | ISO currency code (default: `ILS`) |
| is_active | Boolean | Whether account is currently tracked |

### Transactions
Core financial transactions with categorization metadata.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| account_id | Integer | FK to accounts |
| date | DateTime | Transaction date |
| amount | Float | Amount (negative for expenses) |
| description | String | Raw transaction description |
| merchant | String | Extracted/cleaned merchant name |
| category_id | Integer | FK to categories (nullable) |
| is_categorized | Boolean | Whether categorization is complete |
| categorization_method | String | `manual`, `rule`, or `llm` |
| categorization_confidence | Float | 0-1 confidence score (for LLM) |
| is_recurring | Boolean | Flagged as recurring transaction |
| recurring_group_id | String | Groups recurring transactions |
| original_currency | String | Currency if converted |
| original_amount | Float | Amount before conversion |
| notes | Text | User notes |
| source_file | String | Original CSV filename |
| source_row | Integer | Row number in source file |

**Indexes:**
- `(date, amount)` — for time-series queries
- `(account_id, date)` — for account statements
- `(category_id, date)` — for category spending reports

### Categories
Hierarchical transaction categories with support for subcategories.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String | Unique category name |
| parent_id | Integer | FK to self (for subcategories) |
| category_type | String | `income` or `expense` |
| icon | String | Emoji or icon name |
| color | String | Hex color code |
| is_system | Boolean | System categories can't be deleted |

**Default Categories:**
- **Income:** Salary, Freelance, Investment Returns
- **Expenses:** Groceries, Dining Out, Transportation, Utilities, Housing, Healthcare, Entertainment, Shopping, Education, Insurance, Subscriptions, etc.

### Budgets
Monthly spending limits per category.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| category_id | Integer | FK to categories |
| amount | Float | Budget limit |
| period | String | `monthly`, `weekly`, `yearly` |
| start_date | DateTime | Budget start date |
| end_date | DateTime | Budget end date (null = ongoing) |
| alert_threshold | Float | Alert when % threshold reached (default: 0.8) |
| is_active | Boolean | Whether budget is currently active |

### Savings Goals
User-defined savings targets.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String | Goal name (e.g., "Vacation Fund") |
| target_amount | Float | Target savings amount |
| current_amount | Float | Current progress toward goal |
| deadline | DateTime | Target completion date (optional) |
| description | Text | Goal description |
| is_completed | Boolean | Whether goal has been reached |

### Categorization Rules
Rule-based auto-categorization engine.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| category_id | Integer | FK to categories |
| rule_type | String | `keyword`, `regex`, `merchant` |
| pattern | String | Pattern to match |
| priority | Integer | Execution order (higher = first) |
| is_active | Boolean | Whether rule is enabled |

**Examples:**
- `keyword` — "שופרסל" → Groceries
- `regex` — `PAZ.*` → Gas (Transportation subcategory)
- `merchant` — exact merchant ID match

## Categorization Flow

1. **Rule-based** — Fast pattern matching against known merchants/keywords
2. **LLM fallback** — Claude API for ambiguous transactions
3. **Manual correction** — User can override any categorization
4. **Learning** — Manual corrections create new rules

## Relationships

```
Account (1) ─────< (N) Transaction
                     │
                     ├─> (1) Category
                     │
Category (1) ────< (N) Budget
     │
     ├─> (N) CategorizationRule
     └─> (1) Category (parent)
```

## Initialization

Run `python init_db.py` to:
1. Create all tables
2. Seed default Israeli categories
3. Set up indexes

## Database Migrations

For schema changes, use Alembic (to be set up in Phase 2+):
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```
