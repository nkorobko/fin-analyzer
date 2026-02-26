# Fin Analyzer

Personal finance analyzer with AI-powered categorization and insights.

## Project Structure

```
fin-analyzer/
├── frontend/          # React + Vite + TypeScript
├── backend/           # Python FastAPI
├── shared/            # Shared types and utilities
└── docs/              # Documentation
```

## Tech Stack

**Frontend**
- React 18
- Vite
- TypeScript
- TailwindCSS
- Recharts (for data visualization)

**Backend**
- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite (local database)
- Anthropic Claude API (for AI categorization)

## Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- pnpm (or npm/yarn)

### Setup

```bash
# Install frontend dependencies
cd frontend
pnpm install

# Install backend dependencies
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development servers
# Terminal 1 (frontend)
cd frontend && pnpm dev

# Terminal 2 (backend)
cd backend && uvicorn main:app --reload
```

## Roadmap

### Phase 1 — Foundation
- [x] Project setup
- [ ] Data model design
- [ ] CSV import pipeline
- [ ] Transaction list view

### Phase 2 — Categorization
- [ ] Rule-based categorization
- [ ] LLM-based categorization
- [ ] Category management UI

### Phase 3 — Visualization & Budgeting
- [ ] Spending dashboard
- [ ] Budget tracking
- [ ] Savings goals

### Phase 4 — Intelligence (AI)
- [ ] Anomaly detection
- [ ] Natural language queries
- [ ] Monthly summaries

### Phase 5 — Polish
- [ ] Multi-currency support
- [ ] Recurring transactions
- [ ] Export & reports
- [ ] Security & encryption
