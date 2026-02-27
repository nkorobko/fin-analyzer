# LLM Categorization Example

## Sample Transaction

**Input:**
```json
{
  "description": "AMZN MKTP US*AB12C3D4",
  "merchant": null,
  "amount": -127.30,
  "date": "2026-01-15"
}
```

## LLM Prompt

```
Analyze this financial transaction and categorize it.

Transaction Details:
- Description: AMZN MKTP US*AB12C3D4
- Merchant: N/A
- Amount: 127.30 ILS (expense)
- Date: 2026-01-15

Available Categories (ID - Name):
- 1 Groceries
- 2 Dining Out
- 3 Transportation
- 4 Shopping
- 5 Entertainment
...

Instructions:
1. Choose the MOST appropriate category from the list above
2. Consider that this is an Israeli transaction (may contain Hebrew text)
3. Common Israeli merchants: שופרסל (groceries), פז (gas), ארומה (coffee), etc.
4. Respond ONLY with valid JSON in this exact format:
{"category_id": <number>, "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}

Your response:
```

## LLM Response

```json
{
  "category_id": 4,
  "confidence": 0.9,
  "reasoning": "Amazon Marketplace purchase - online shopping"
}
```

## Result

The transaction is categorized as:
- **Category:** Shopping (ID: 4)
- **Method:** llm
- **Confidence:** 0.9

## Example: Hebrew Transaction

**Input:**
```json
{
  "description": "רשת יש - סניף קניון עזריאלי",
  "merchant": "רשת יש",
  "amount": -89.50,
  "date": "2026-01-20"
}
```

**LLM Response:**
```json
{
  "category_id": 1,
  "confidence": 0.95,
  "reasoning": "Yesh supermarket - grocery store chain"
}
```

**Result:** Categorized as Groceries

## Example: Ambiguous Transaction

**Input:**
```json
{
  "description": "PayPal *SUBSCRIPTION",
  "merchant": null,
  "amount": -39.90,
  "date": "2026-01-25"
}
```

**LLM Response:**
```json
{
  "category_id": 15,
  "confidence": 0.6,
  "reasoning": "PayPal subscription payment - likely digital service, but specific service unknown"
}
```

**Result:** Categorized as Subscriptions, but lower confidence suggests manual review may be needed.
