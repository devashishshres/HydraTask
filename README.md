# HydraTask — Task Context Hydrator

> Hackathon project for "Reducing Workplace Friction Through Intelligent Task Orchestration"

## What it does
Takes a vague task description (e.g., "Fix the slow database") and automatically enriches it with relevant technical context — documentation links, code repo, team owner, and concrete next steps.

## Tech Stack
- **Frontend:** Next.js 14 (TypeScript, Tailwind CSS, App Router)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **AI:** Claude (Anthropic)

## Project Structure
```
HydraTask/
├── frontend/    ← Next.js app (runs on port 3000)
├── backend/     ← FastAPI app (runs on port 8000)
└── README.md
```

## Getting Started

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
