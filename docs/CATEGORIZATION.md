# Transaction Categorization

Fin Analyzer uses a two-tier categorization system: **rule-based** (fast, pattern matching) and **LLM-based** (fallback for ambiguous transactions).

## Rule-Based Categorization

### How It Works

1. **Pattern Matching** — Rules match against transaction description and merchant name
2. **Priority Order** — Rules execute in descending priority (highest first)
3. **First Match Wins** — Once a rule matches, categorization stops
4. **Automatic Application** — Rules are applied during import and can be run on existing transactions

### Rule Types

#### Keyword
Simple substring matching (case-insensitive).

**Example:**
- Pattern: `פז`
- Matches: "פז - תחנת דלק", "תדלוק פז", "PAZ STATION"

#### Regex
Regular expression matching for complex patterns.

**Example:**
- Pattern: `^amzn.*`
- Matches: "AMZN MKTP US", "AMZN Marketplace", etc.

#### Merchant
Exact match on the cleaned merchant field.

**Example:**
- Pattern: `shufersal`
- Matches only exact merchant name (after normalization)

### Default Israeli Rules

The system comes pre-configured with 40+ rules for common Israeli merchants:

**Groceries:**
- שופרסל, רמי לוי, יינות ביתן, ויקטורי, סופר, מכולת

**Gas Stations:**
- פז, סונול, דלק, דור אלון

**Dining:**
- ארומה, קפה גרג, מקדונלד

**Healthcare:**
- סופר פארם, ניו פארם, בית מרקחת

**Public Transit:**
- רב קו, אגד, דן

**Utilities:**
- חברת חשמל, מקורות, בזק, סלקום, פרטנר

**Subscriptions:**
- Netflix, Spotify, Amazon

**And more...**

## Priority System

Rules with higher priority execute first. This allows:

1. **Specific > General** — High-priority exact matches override low-priority keywords
2. **Custom Overrides** — User-created rules can override defaults by setting higher priority
3. **Conflict Resolution** — When multiple patterns could match, priority determines the winner

### Recommended Priority Ranges

- **100-200:** Exact merchant matches (highest confidence)
- **50-99:** Common keyword patterns
- **0-49:** General/fallback patterns

## API Endpoints

### Get All Rules
```
GET /api/categorization/rules
```

Returns all categorization rules sorted by priority.

### Create Rule
```
POST /api/categorization/rules
```

**Body:**
```json
{
  "category_id": 5,
  "rule_type": "keyword",
  "pattern": "sushi",
  "priority": 80
}
```

### Update Rule
```
PATCH /api/categorization/rules/{rule_id}
```

**Body:**
```json
{
  "priority": 90,
  "is_active": true
}
```

### Delete Rule
```
DELETE /api/categorization/rules/{rule_id}
```

### Categorize All Uncategorized
```
POST /api/categorization/categorize-all
```

Runs categorization on all transactions that don't have a category.

**Response:**
```json
{
  "success": true,
  "total": 150,
  "categorized": 120,
  "failed": 30,
  "by_rule": 120,
  "by_llm": 0
}
```

### Categorize Single Transaction
```
POST /api/categorization/transactions/{transaction_id}/categorize
```

Attempts to categorize a specific transaction.

## Automatic Categorization

### During Import

Transactions are automatically categorized as they're imported:

1. CSV file is parsed
2. Transactions are created in database
3. Rule engine runs on each transaction
4. Matching category is assigned (if found)

### Manual Re-categorization

You can re-run categorization at any time:

- **All uncategorized:** Use the "Categorize All" button
- **Single transaction:** Click "Re-categorize" on the transaction
- **API:** Call `/api/categorization/categorize-all` or `/transactions/{id}/categorize`

## Performance

- **Rules are cached** in memory for fast matching
- **Average categorization time:** <1ms per transaction
- **Bulk operations:** Can categorize thousands of transactions in seconds

Cache is automatically invalidated when rules are added/updated/deleted.

## Custom Rules

### Adding Your Own Rules

1. Go to **Settings** → **Categorization Rules**
2. Click **Add Rule**
3. Select category
4. Choose rule type (keyword/regex/merchant)
5. Enter pattern
6. Set priority (higher = executes first)
7. Save

### Pattern Tips

**For Keywords:**
- Use lowercase (matching is case-insensitive)
- Be specific enough to avoid false positives
- Common words like "payment" or "transfer" may match too broadly

**For Regex:**
- Test your pattern first (use regex101.com)
- Use `^` and `$` for exact matches
- Use `.*` for wildcards
- Escape special characters

**Examples:**

```
# Match any Netflix transaction
Pattern: netflix
Type: keyword

# Match Amazon Marketplace specifically
Pattern: ^amzn mktp
Type: regex

# Match Israeli gas stations
Pattern: (פז|סונול|דלק)
Type: regex
```

## Troubleshooting

### Rule Not Matching

**Check:**
1. Pattern spelling (case doesn't matter, but spelling does)
2. Rule is active (`is_active = true`)
3. Rule priority isn't being overridden by a higher-priority rule
4. Pattern type matches your use case

### Too Many False Positives

**Solution:**
- Make pattern more specific
- Lower the priority so it doesn't override better matches
- Use regex with anchors (`^`, `$`) for exact matching

### Hebrew Text Issues

**Ensure:**
- CSV file is UTF-8 encoded
- Pattern uses actual Hebrew characters (not transliteration)
- No extra spaces or invisible characters in pattern

## Next: LLM Categorization

For transactions that don't match any rules, Phase 2 (Issue #6) adds LLM-based categorization using Claude API.
