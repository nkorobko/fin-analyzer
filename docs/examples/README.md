# Example CSV Files

These are sample CSV files demonstrating the format from each supported Israeli bank.

## Files

- `leumi_example.csv` — Bank Leumi format
- `hapoalim_example.csv` — Bank Hapoalim format
- `max_example.csv` — Max credit card format

## Usage

These files can be used to:
1. Test the import functionality
2. Understand the expected CSV structure
3. Debug parser issues

**Note:** These are sanitized example files with fake data. Real bank exports will contain your actual transaction data.

## Field Descriptions

### Leumi
- **תאריך** — Transaction date (DD/MM/YYYY)
- **תיאור** — Description
- **אסמכתא** — Reference number
- **חובה** — Debit amount
- **זכות** — Credit amount
- **יתרה** — Balance after transaction

### Hapoalim
- **תאריך** — Transaction date
- **תיאור** — Description
- **שם בית עסק** — Merchant name
- **סכום חיוב** — Debit amount
- **סכום זיכוי** — Credit amount
- **יתרה** — Balance

### Max (Credit Card)
- **תאריך רכישה** — Purchase date
- **שם בית עסק** — Merchant name
- **סכום** — Amount in ILS
- **מטבע** — Currency
- **סכום מקורי** — Original amount (foreign currency)
- **תאריך חיוב** — Billing date
