# CSV Import Guide

## Supported Banks

Fin Analyzer supports CSV exports from the following Israeli banks and credit card companies:

### Banks
- **Bank Leumi** — Checking and savings accounts
- **Bank Hapoalim** — Checking and savings accounts
- **Discount Bank** — All account types

### Credit Cards
- **Max (Leumi Card)** — Credit card statements
- **Cal (Israel Credit Cards)** — Credit card statements

## How to Export from Your Bank

### Bank Leumi
1. Log in to Leumi Online
2. Go to **Accounts** → Select your account
3. Click **Download transactions**
4. Choose **CSV format**
5. Select date range and download

### Bank Hapoalim
1. Log in to online banking
2. Select **Account transactions**
3. Choose date range
4. Click **Export to Excel/CSV**

### Discount Bank
1. Log in to banking portal
2. Navigate to **Transaction history**
3. Select **Export** → **CSV**

### Max Credit Card
1. Log in to Max website
2. Go to **Transactions**
3. Click **Export to Excel**
4. Save as CSV

### Cal Credit Card
1. Log in to Cal portal
2. View **Statement**
3. Click **Download CSV**

## Import Process

### Automatic Format Detection

Fin Analyzer automatically detects which bank format your CSV uses. Simply:

1. Go to **Import** page
2. Select your account
3. Upload the CSV file
4. Click **Import**

The system will:
- Auto-detect the bank format
- Parse the transactions
- Skip duplicates (if enabled)
- Categorize transactions (Phase 2+)

### Manual Bank Selection

If auto-detection fails, you can manually specify the bank:

```bash
# API example
curl -X POST http://localhost:8000/api/import/upload \
  -F "file=@transactions.csv" \
  -F "account_id=1" \
  -F "bank=Leumi"
```

## CSV Format Requirements

### Common Fields Across All Banks

All parsers expect at least:
- **Date** — Transaction date
- **Description** — Transaction description or merchant name
- **Amount** — Transaction amount (debit/credit or combined)

### Encoding

The system supports multiple encodings common in Israeli banks:
- UTF-8
- Windows-1255 (Hebrew)
- ISO-8859-8

Encoding is auto-detected.

### Date Formats

Supported date formats:
- `DD/MM/YYYY` (most common)
- `DD-MM-YYYY`
- `YYYY-MM-DD`
- `DD.MM.YYYY`
- `DD/MM/YY`

## Duplicate Detection

By default, the import process skips duplicate transactions based on:
- Account ID
- Date
- Amount
- Description

This prevents importing the same file twice or overlapping date ranges.

To disable duplicate checking, set `skip_duplicates=false` in the API call.

## Troubleshooting

### "Could not detect bank format"

**Cause:** CSV file doesn't match any known format.

**Solution:**
1. Check that the file is a valid CSV export from your bank
2. Ensure Hebrew characters are properly encoded
3. Try manually specifying the bank name

### "File does not match [Bank] format"

**Cause:** CSV structure doesn't match expected columns.

**Solution:**
1. Download a fresh export from the bank
2. Don't modify the CSV file (no column reordering, renaming, etc.)
3. Check that you selected the correct bank

### Encoding issues (gibberish Hebrew text)

**Cause:** Wrong encoding detection.

**Solution:**
1. Save the CSV with UTF-8 encoding
2. Open the CSV in Excel, Save As → CSV UTF-8

## API Reference

### Get Supported Banks
```
GET /api/import/supported-banks
```

Returns list of supported bank formats.

### Detect Format
```
POST /api/import/detect-format
```

Upload a CSV file to detect its format without importing.

### Upload & Import
```
POST /api/import/upload
```

**Parameters:**
- `file` (file) — CSV file
- `account_id` (int) — Target account ID
- `bank` (string, optional) — Bank name (auto-detect if omitted)
- `skip_duplicates` (bool, default: true) — Skip duplicate transactions

**Response:**
```json
{
  "success": true,
  "filename": "transactions.csv",
  "total_parsed": 150,
  "imported": 145,
  "skipped_duplicates": 5,
  "errors": 0,
  "bank": "Leumi"
}
```

## Example CSV Files

See `/docs/examples/` for sample CSV files for each supported bank format.
