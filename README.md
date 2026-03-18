# HydraTask

**Turn vague tasks into structured action cards — instantly.**

HydraTask takes an ambiguous task description like *"Fix the slow database"* or *"Dashboard is showing wrong numbers"* and enriches it with everything an engineer needs to act: the right owner, relevant documentation, the service repo, and a clear set of steps.

---

## The Problem

In most engineering teams, tasks are created in plain language with no context attached. Someone files a ticket like *"payments are broken"* — and the person who picks it up spends the first 30 minutes figuring out:

- Which service is responsible?
- Who owns it?
- Where is the repo?
- What docs exist?
- What should I actually do first?

That friction compounds across every task, every team, every day.

## The Solution

HydraTask connects to your internal service registry and, when given a vague task, uses AI to:

1. Match the task to the most relevant services in your org
2. Identify the owning team
3. Pull the right documentation links
4. Generate a concrete, ordered set of steps

The result is a structured **action card** — ready to assign, act on, or drop into a ticket.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16 (TypeScript, Tailwind CSS v4, App Router) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL (via SQLAlchemy) |
| AI | Google Gemini 2.5 Flash |
| Fonts | Bitter · Work Sans · Fira Code |

---

## Project Structure

```
HydraTask/
├── frontend/               ← Next.js app (port 3000)
│   └── app/
│       ├── page.tsx        ← Main UI + ResultCard component
│       ├── layout.tsx      ← Font loading + root layout
│       └── globals.css     ← Theme variables + animations
│
└── backend/                ← FastAPI app (port 8000)
    ├── main.py             ← API routes + CORS config
    ├── hydrator.py         ← AI routing logic + token optimisation
    ├── database.py         ← SQLAlchemy models (Team, Service, Doc)
    ├── schemas.py          ← Pydantic request/response shapes
    ├── seed.py             ← Mock company data (8 teams, 10 services, 18 docs)
    ├── Procfile            ← Railway start command
    └── requirements.txt
```

---

## How It Works

1. **Pre-filter** — keyword scoring ranks all services against the task (no stop words, weighted by name / description / ownership). Only the top 3 are sent to the model.
2. **Compact prompt** — tight instruction set, no filler, strict JSON output format.
3. **Gemini call** — capped at 400 output tokens with low temperature (0.3) to keep responses focused.
4. **Parse + return** — JSON is parsed into a typed `ActionCard`. If the API call fails for any reason, a mock fallback is returned so the app never crashes.

This approach reduces token usage by ~60% compared to sending the full service database.

---

## Running Locally

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL running locally
- A [Google Gemini API key](https://aistudio.google.com/apikey)

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```
DATABASE_URL=postgresql://hydrauser:hydrapass@localhost:5432/hydradb
GEMINI_API_KEY=your_key_here
```

Set up the database:

```bash
# Create DB user and database (run once)
sudo -u postgres psql -c "CREATE USER hydrauser WITH PASSWORD 'hydrapass';"
sudo -u postgres psql -c "CREATE DATABASE hydradb OWNER hydrauser;"

# Seed mock company data
python seed.py
```

Start the backend:

```bash
uvicorn main:app --reload
# API available at http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# App available at http://localhost:3000
```

---

---

## API Reference

### `GET /`
Health check.
```json
{ "status": "HydraTask backend is running" }
```

### `POST /hydrate`
Takes a task description, returns a structured action card.

**Request:**
```json
{ "task": "Fix the slow database queries on the analytics dashboard" }
```

**Response:**
```json
{
  "objective": "Investigate and resolve slow query performance in the analytics pipeline",
  "steps": [
    "Check Grafana dashboards for query latency spikes",
    "Review recent changes to the data-pipeline service",
    "Profile slow queries and add missing indexes"
  ],
  "docs": ["https://docs.acme.com/data/pipeline-arch"],
  "assigned_to": "Dan Kim",
  "repo": "https://github.com/acme-corp/data-pipeline",
  "original_task": "Fix the slow database queries on the analytics dashboard"
}
```

---

## Seeded Data

The mock database covers a realistic cross-functional engineering org:

| Team Member | Role | Owns |
|-------------|------|------|
| Alice Chen | Backend Lead | Payments, billing, invoicing |
| Bob Martinez | DevOps / SRE | Infrastructure, CI/CD, monitoring |
| Carol Singh | Frontend Lead | Dashboard, user portal, web UI |
| Dan Kim | Data Engineer | Analytics, data pipeline, warehouse |
| Maya Patel | Mobile Lead | iOS/Android app, push notifications |
| James Liu | Security Engineer | Auth, OAuth, SSO, JWT, MFA |
| Sofia Torres | Platform Engineer | API gateway, rate limiting, service mesh |
| Ethan Brooks | Backend Engineer | Notifications, email, SMS, search |
