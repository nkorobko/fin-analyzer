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

## LLM-Based Categorization

For transactions that don't match any rule, the system can use **Claude AI** to intelligently categorize them.

### How It Works

1. **Rule Engine First** — Always try rule-based matching first (fast, free)
2. **LLM Fallback** — If no rule matches, optionally call Claude API
3. **Confidence Score** — Claude returns a 0.0-1.0 confidence score
4. **Category Validation** — System verifies the AI's category choice exists

### When to Use LLM

**Use LLM for:**
- New/unknown merchants not covered by rules
- Ambiguous transaction descriptions
- One-time or irregular transactions
- Foreign merchants
- Complex or cryptic descriptions (e.g., "AMZN MKTP US*AB12C3D4")

**Don't use LLM for:**
- High-volume imports (can be expensive)
- Transactions with clear patterns (create a rule instead)
- When speed is critical

### API Usage

#### Enable LLM for Bulk Categorization
```
POST /api/categorization/categorize-all?use_llm=true
```

**Response:**
```json
{
  "success": true,
  "total": 150,
  "categorized": 140,
  "failed": 10,
  "by_rule": 120,
  "by_llm": 20
}
```

#### Enable LLM for Single Transaction
```
POST /api/categorization/transactions/{id}/categorize?use_llm=true
```

### Configuration

Set your Anthropic API key in `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Get an API key at: https://console.anthropic.com/

### Cost Considerations

Claude API pricing (as of 2024):
- **Input:** ~$3 per million tokens
- **Output:** ~$15 per million tokens

Typical transaction categorization:
- ~150 tokens per request
- **Cost:** ~$0.0005 per transaction

**Example costs:**
- 100 transactions: ~$0.05
- 1,000 transactions: ~$0.50
- 10,000 transactions: ~$5.00

**Recommendation:** Use rules for recurring transactions, reserve LLM for unknowns.

### Model Used

- **Model:** claude-3-5-sonnet-20241022
- **Temperature:** 0 (deterministic)
- **Max tokens:** 200 (JSON response only)

### Prompt Design

The LLM receives:
- Transaction description
- Merchant name (if available)
- Amount and whether it's income/expense
- Date
- Full list of available categories

It responds with structured JSON:
```json
{
  "category_id": 5,
  "confidence": 0.85,
  "reasoning": "Coffee shop purchase"
}
```

### Performance

- **Average latency:** 1-2 seconds per transaction
- **Success rate:** ~95% for clear descriptions
- **Fallback:** If LLM fails, transaction remains uncategorized

### Hebrew Support

Claude handles Hebrew text naturally:
- Can understand Hebrew merchant names (שופרסל, פז, etc.)
- Recognizes mixed Hebrew-English descriptions
- Aware of Israeli context and common merchants

### Best Practices

1. **Build Rules First** — Create rules for your most common transactions
2. **LLM for Exceptions** — Use AI only for what rules can't handle
3. **Review AI Results** — Check confidence scores, correct mistakes
4. **Create Rules from Patterns** — If LLM categorizes the same merchant repeatedly, create a rule
5. **Monitor Costs** — Track API usage if processing large volumes

### Troubleshooting

**LLM Not Working:**
- Check that `ANTHROPIC_API_KEY` is set in `.env`
- Verify API key is valid
- Check API quota/billing status

**Low Confidence Scores:**
- Descriptions may be too vague
- Multiple categories could apply
- Consider manual review for scores <0.7

**Wrong Categories:**
- LLM may misinterpret ambiguous descriptions
- Create specific rules to override
- Manually correct and log patterns

### Workflow Recommendation

**Initial Import:**
1. Import CSV → auto-categorize with rules only
2. Review uncategorized transactions
3. For one-time/unknown merchants → use LLM
4. For recurring patterns → create new rules
5. Re-run bulk categorization

**Ongoing Use:**
- Weekly: Review new uncategorized transactions
- Monthly: Analyze LLM results, create rules for common patterns
- Quarterly: Audit rule coverage, optimize for better accuracy
