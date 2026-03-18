"""
Core hydration logic.

Takes a vague task string, pre-filters company data by relevance,
sends a compact prompt to Gemini, and returns a structured ActionCard.

Token optimisation strategy:
  1. Pre-filter: score services by keyword overlap with the task,
     send only the top 3 matches instead of the full database.
  2. Compact prompt: tight instructions, no filler text.
  3. Capped output: max_output_tokens stops Gemini over-explaining.
"""

import os
import re
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from database import Team, Service, Doc
from schemas import ActionCard

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Words that carry no signal for matching (filtered out before scoring)
_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "have", "has", "do", "does", "not", "for", "in", "on", "at",
    "to", "of", "and", "or", "with", "that", "this", "it", "its",
    "some", "all", "very", "just", "also", "can", "will", "would",
    "should", "could", "may", "might", "our", "we", "i", "you",
}


def _keywords(text: str) -> set[str]:
    """Extract meaningful lowercase words from a text string."""
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if w not in _STOP_WORDS and len(w) > 2}


def get_relevant_context(task: str, db: Session, top_n: int = 3) -> str:
    """
    Score every service against the task keywords and return only the
    top_n most relevant services — with their owner and docs.

    Scoring:
      +2 for each keyword that appears in the service description
      +3 for each keyword that appears in the team's 'owns' field
      +1 for each keyword that appears in the service name
    """
    task_keywords = _keywords(task)
    services = db.query(Service).all()

    scored = []
    for svc in services:
        owner = db.query(Team).filter(Team.id == svc.owner_id).first()
        score = 0
        score += 2 * len(task_keywords & _keywords(svc.description or ""))
        score += 3 * len(task_keywords & _keywords(owner.owns if owner else ""))
        score += 1 * len(task_keywords & _keywords(svc.name))
        scored.append((score, svc, owner))

    # Sort by score descending; take top N (always include at least 1)
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_n]

    # Build compact context string for just the selected services
    lines = []
    for _, svc, owner in top:
        owner_name = owner.name if owner else "Unknown"
        owner_role = owner.role if owner else ""
        docs = db.query(Doc).filter(Doc.service_id == svc.id).all()
        doc_urls = ", ".join(d.url for d in docs)
        lines.append(
            f"- {svc.name} | owner: {owner_name} ({owner_role}) | "
            f"desc: {svc.description} | repo: {svc.repo_url} | docs: {doc_urls}"
        )

    return "\n".join(lines)


def build_prompt(task: str, context: str) -> str:
    """Compact prompt — clear instructions, no filler, strict JSON output."""
    return (
        f'You are a task router. Given a task and company service data, '
        f'return a JSON action card. Be concise.\n\n'
        f'SERVICES:\n{context}\n\n'
        f'TASK: "{task}"\n\n'
        f'Reply with ONLY this JSON (no markdown):\n'
        f'{{"objective":"...","steps":["...","...","..."],'
        f'"docs":["url1"],"assigned_to":"name","repo":"url"}}'
    )


def mock_hydrate(task: str, db: Session) -> ActionCard:
    """Fallback when the Gemini API is unavailable."""
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
    """
    Main function — takes a vague task and returns a structured ActionCard.

    Flow:
      1. Pre-filter DB to top 3 relevant services (reduces prompt size ~60%)
      2. Build a compact prompt
      3. Call Gemini with a capped output token limit
      4. Parse JSON response into ActionCard
    """
    context = get_relevant_context(task, db, top_n=3)
    prompt = build_prompt(task, context)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=400,   # enough for a full action card, stops over-generation
                temperature=0.3,         # lower = more focused, less random padding
            ),
        )
        raw_text = response.text.strip()

        # Strip markdown code fences if Gemini adds them
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            raw_text = raw_text.rsplit("```", 1)[0]

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
        return mock_hydrate(task, db)
