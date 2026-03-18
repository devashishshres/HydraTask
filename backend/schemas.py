"""
Pydantic models for API request and response shapes.

HydrateRequest  — what the user sends (a vague task description)
ActionCard      — what the user gets back (the enriched, structured output)
"""

from pydantic import BaseModel


class HydrateRequest(BaseModel):
    task: str  # e.g. "Fix the slow database"


class ActionCard(BaseModel):
    objective: str                # clear, one-line goal
    steps: list[str]             # 3 concrete technical steps
    docs: list[str]              # relevant documentation URLs
    assigned_to: str             # team member who owns this area
    repo: str                    # relevant code repository
    original_task: str           # the raw input for reference
