"""
Core hydration logic.

Takes a vague task string, pulls company context from the DB,
sends both to Gemini, and returns a structured ActionCard.
"""

import os
import json
from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from database import Team, Service, Doc
from schemas import ActionCard

load_dotenv()

# Initialize the new google-genai client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_company_context(db: Session) -> str:
    """Pull all company data from DB and format it as a string for the AI prompt."""
    teams = db.query(Team).all()
    services = db.query(Service).all()
    docs = db.query(Doc).all()

    context = "=== COMPANY TEAM MEMBERS ===\n"
    for t in teams:
        context += f"- {t.name} | Role: {t.role} | Owns: {t.owns}\n"

    context += "\n=== SERVICES ===\n"
    for s in services:
        owner = db.query(Team).filter(Team.id == s.owner_id).first()
        owner_name = owner.name if owner else "Unknown"
        context += f"- {s.name} | Repo: {s.repo_url} | Owner: {owner_name} | {s.description}\n"

    context += "\n=== DOCUMENTATION ===\n"
    for d in docs:
        svc = db.query(Service).filter(Service.id == d.service_id).first()
        svc_name = svc.name if svc else "General"
        context += f"- {d.title} | URL: {d.url} | Service: {svc_name}\n"

    return context


def build_prompt(task: str, company_context: str) -> str:
    """Build the prompt that tells Gemini what to do and how to respond."""
    return f"""You are a task hydrator for a software team. A user has submitted a vague task.
Your job is to analyze it, cross-reference it with the company data below, and return
a structured action card.

COMPANY DATA:
{company_context}

VAGUE TASK: "{task}"

Respond with ONLY valid JSON in this exact format (no markdown, no extra text):
{{
    "objective": "A clear, one-line description of what needs to be done",
    "steps": ["Step 1 detail", "Step 2 detail", "Step 3 detail"],
    "docs": ["url1", "url2"],
    "assigned_to": "Name of the team member who owns this area",
    "repo": "The relevant repository URL"
}}
"""


def mock_hydrate(task: str, db: Session) -> ActionCard:
    """
    Fallback mock response using real data from the DB.
    Used when the Gemini API is unavailable.
    Returns the first service/team/doc from the DB so the shape is realistic.
    """
    service = db.query(Service).first()
    team = db.query(Team).first()
    doc = db.query(Doc).first()

    return ActionCard(
        objective=f"Investigate and resolve: '{task}'",
        steps=[
            f"Check logs and metrics for {service.name if service else 'the relevant service'}",
            "Identify the root cause by reviewing recent changes in the repository",
            "Apply the fix, write a regression test, and deploy to staging for verification",
        ],
        docs=[doc.url if doc else "https://docs.acme.com"],
        assigned_to=team.name if team else "Team Lead",
        repo=service.repo_url if service else "https://github.com/acme-corp",
        original_task=task,
    )


def hydrate_task(task: str, db: Session) -> ActionCard:
    """Main function — takes a vague task and returns a structured ActionCard."""
    company_context = get_company_context(db)
    prompt = build_prompt(task, company_context)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )
        raw_text = response.text.strip()

        # Clean up response in case Gemini wraps it in markdown code blocks
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]  # remove opening ```json
            raw_text = raw_text.rsplit("```", 1)[0]  # remove closing ```

        parsed = json.loads(raw_text)

        return ActionCard(
            objective=parsed["objective"],
            steps=parsed["steps"],
            docs=parsed["docs"],
            assigned_to=parsed["assigned_to"],
            repo=parsed["repo"],
            original_task=task,
        )

    except Exception:
        # Gemini unavailable (quota/key issue) — fall back to mock response
        return mock_hydrate(task, db)
