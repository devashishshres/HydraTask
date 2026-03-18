"""
Seed script — populates the database with mock company data.

Run once:  python seed.py

This creates realistic-looking teams, services, and docs that
the AI hydrator can reference when enriching vague tasks.
"""

from database import Base, engine, SessionLocal, Team, Service, Doc


def seed():
    # Create all tables (drops nothing — safe to re-run)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Skip if data already exists
    if db.query(Team).first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    # --- Team members ---
    alice = Team(name="Alice Chen", role="Backend Lead", owns="payments, billing")
    bob = Team(name="Bob Martinez", role="DevOps Engineer", owns="infrastructure, CI/CD")
    carol = Team(name="Carol Singh", role="Frontend Lead", owns="dashboard, user portal")
    dan = Team(name="Dan Kim", role="Data Engineer", owns="analytics, data pipeline")

    db.add_all([alice, bob, carol, dan])
    db.flush()  # assigns IDs before we reference them

    # --- Services ---
    payments = Service(
        name="payments-service",
        repo_url="https://github.com/acme-corp/payments-service",
        description="Handles all payment processing, billing cycles, and invoicing",
        owner_id=alice.id,
    )
    infra = Service(
        name="infra-platform",
        repo_url="https://github.com/acme-corp/infra-platform",
        description="Kubernetes cluster management, deployment pipelines, monitoring",
        owner_id=bob.id,
    )
    dashboard = Service(
        name="user-dashboard",
        repo_url="https://github.com/acme-corp/user-dashboard",
        description="Customer-facing dashboard with analytics, settings, and notifications",
        owner_id=carol.id,
    )
    pipeline = Service(
        name="data-pipeline",
        repo_url="https://github.com/acme-corp/data-pipeline",
        description="ETL pipeline for ingesting, transforming, and storing analytics data",
        owner_id=dan.id,
    )

    db.add_all([payments, infra, dashboard, pipeline])
    db.flush()

    # --- Documentation ---
    docs = [
        Doc(title="Payment Gateway Integration Guide", url="https://docs.acme.com/payments/gateway", service_id=payments.id),
        Doc(title="Billing API Reference", url="https://docs.acme.com/payments/billing-api", service_id=payments.id),
        Doc(title="Kubernetes Deployment Runbook", url="https://docs.acme.com/infra/k8s-runbook", service_id=infra.id),
        Doc(title="CI/CD Pipeline Configuration", url="https://docs.acme.com/infra/cicd-config", service_id=infra.id),
        Doc(title="Dashboard Component Library", url="https://docs.acme.com/dashboard/components", service_id=dashboard.id),
        Doc(title="Data Pipeline Architecture", url="https://docs.acme.com/data/pipeline-arch", service_id=pipeline.id),
    ]

    db.add_all(docs)
    db.commit()
    db.close()

    print("Database seeded successfully with mock company data.")


if __name__ == "__main__":
    seed()
