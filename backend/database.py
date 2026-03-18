"""
Database connection and table models.

Tables:
- teams: People in the company (name, role, what they own)
- services: Internal systems/services (name, repo, description)
- docs: Documentation links (title, url, related service)

All three tables are what the AI queries to "hydrate" a vague task.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# --- Models ---

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    owns = Column(String(200), nullable=False)  # what system/area they own


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    repo_url = Column(String(300))
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("teams.id"))

    owner = relationship("Team")


class Doc(Base):
    __tablename__ = "docs"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    url = Column(String(300), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"))

    service = relationship("Service")


def get_db():
    """FastAPI dependency — yields a DB session, auto-closes after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
