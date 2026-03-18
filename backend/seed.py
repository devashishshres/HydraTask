"""
Seed script — populates the database with mock company data.

Run:         python seed.py
Reset & re-seed: python seed.py --reset

Covers 8 team members, 10 services, and 18 docs across:
payments, infrastructure, frontend, data, mobile, auth,
notifications, API gateway, search, and security.
"""

import sys
from database import Base, engine, SessionLocal, Team, Service, Doc


def seed(reset=False):
    db = SessionLocal()

    if reset:
        # Drop all tables and recreate fresh
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

    Base.metadata.create_all(bind=engine)

    # Skip if data already exists and not resetting
    if not reset and db.query(Team).first():
        print("Database already seeded. Run with --reset to reseed.")
        db.close()
        return

    # ── Team Members ──────────────────────────────────────────────────────────

    alice   = Team(name="Alice Chen",     role="Backend Lead",            owns="payments, billing, invoicing")
    bob     = Team(name="Bob Martinez",   role="DevOps / SRE",            owns="infrastructure, CI/CD, monitoring, on-call")
    carol   = Team(name="Carol Singh",    role="Frontend Lead",           owns="dashboard, user portal, web app UI")
    dan     = Team(name="Dan Kim",        role="Data Engineer",           owns="analytics, data pipeline, reporting, data warehouse")
    maya    = Team(name="Maya Patel",     role="Mobile Lead",             owns="iOS app, Android app, mobile auth, push notifications")
    james   = Team(name="James Liu",      role="Security Engineer",       owns="auth service, OAuth, SSO, JWT, security audits, compliance")
    sofia   = Team(name="Sofia Torres",   role="Platform Engineer",       owns="API gateway, rate limiting, service mesh, developer tools")
    ethan   = Team(name="Ethan Brooks",   role="Backend Engineer",        owns="notifications service, email delivery, SMS, webhooks, search service")

    db.add_all([alice, bob, carol, dan, maya, james, sofia, ethan])
    db.flush()

    # ── Services ──────────────────────────────────────────────────────────────

    payments = Service(
        name="payments-service",
        repo_url="https://github.com/acme-corp/payments-service",
        description="Handles all payment processing, billing cycles, invoicing, refunds, and Stripe integration",
        owner_id=alice.id,
    )
    infra = Service(
        name="infra-platform",
        repo_url="https://github.com/acme-corp/infra-platform",
        description="Kubernetes cluster management, Terraform configs, deployment pipelines, and cloud infrastructure",
        owner_id=bob.id,
    )
    dashboard = Service(
        name="user-dashboard",
        repo_url="https://github.com/acme-corp/user-dashboard",
        description="Customer-facing web dashboard — settings, account management, usage stats, and billing UI",
        owner_id=carol.id,
    )
    pipeline = Service(
        name="data-pipeline",
        repo_url="https://github.com/acme-corp/data-pipeline",
        description="ETL pipeline for ingesting, transforming, and loading analytics data into the data warehouse",
        owner_id=dan.id,
    )
    mobile = Service(
        name="mobile-app",
        repo_url="https://github.com/acme-corp/mobile-app",
        description="React Native iOS and Android app — handles login, onboarding, push notifications, and offline mode",
        owner_id=maya.id,
    )
    auth = Service(
        name="auth-service",
        repo_url="https://github.com/acme-corp/auth-service",
        description="OAuth2, SSO, JWT token issuing/refresh, session management, MFA, and password reset flows",
        owner_id=james.id,
    )
    gateway = Service(
        name="api-gateway",
        repo_url="https://github.com/acme-corp/api-gateway",
        description="Central API gateway — handles routing, rate limiting, request validation, and API versioning",
        owner_id=sofia.id,
    )
    notifications = Service(
        name="notifications-service",
        repo_url="https://github.com/acme-corp/notifications-service",
        description="Sends transactional emails, SMS alerts, in-app notifications, and webhook events to external systems",
        owner_id=ethan.id,
    )
    search = Service(
        name="search-service",
        repo_url="https://github.com/acme-corp/search-service",
        description="Elasticsearch-based full-text search across users, transactions, and content — handles indexing and queries",
        owner_id=ethan.id,
    )
    monitoring = Service(
        name="monitoring-platform",
        repo_url="https://github.com/acme-corp/monitoring-platform",
        description="Prometheus, Grafana, and PagerDuty integration — tracks uptime, error rates, latency, and on-call alerts",
        owner_id=bob.id,
    )

    db.add_all([payments, infra, dashboard, pipeline, mobile, auth, gateway, notifications, search, monitoring])
    db.flush()

    # ── Documentation ─────────────────────────────────────────────────────────

    docs = [
        # Payments
        Doc(title="Payment Gateway Integration Guide",   url="https://docs.acme.com/payments/gateway",         service_id=payments.id),
        Doc(title="Billing & Invoicing API Reference",   url="https://docs.acme.com/payments/billing-api",     service_id=payments.id),
        Doc(title="Refund & Dispute Handling Runbook",   url="https://docs.acme.com/payments/refunds",         service_id=payments.id),

        # Infrastructure
        Doc(title="Kubernetes Deployment Runbook",       url="https://docs.acme.com/infra/k8s-runbook",        service_id=infra.id),
        Doc(title="CI/CD Pipeline Configuration Guide",  url="https://docs.acme.com/infra/cicd-config",        service_id=infra.id),

        # Dashboard
        Doc(title="Dashboard Component Library",         url="https://docs.acme.com/dashboard/components",     service_id=dashboard.id),
        Doc(title="Frontend Deployment & Release Guide", url="https://docs.acme.com/dashboard/releases",       service_id=dashboard.id),

        # Data
        Doc(title="Data Pipeline Architecture Overview", url="https://docs.acme.com/data/pipeline-arch",       service_id=pipeline.id),
        Doc(title="Data Warehouse Schema Reference",     url="https://docs.acme.com/data/warehouse-schema",    service_id=pipeline.id),

        # Mobile
        Doc(title="Mobile App Build & Release Guide",    url="https://docs.acme.com/mobile/build-release",     service_id=mobile.id),
        Doc(title="Push Notification Setup (iOS/Android)", url="https://docs.acme.com/mobile/push-notifications", service_id=mobile.id),

        # Auth
        Doc(title="OAuth2 & SSO Integration Guide",      url="https://docs.acme.com/auth/oauth-sso",           service_id=auth.id),
        Doc(title="JWT Token Lifecycle & Refresh Flows", url="https://docs.acme.com/auth/jwt-lifecycle",       service_id=auth.id),
        Doc(title="MFA Setup & Troubleshooting",         url="https://docs.acme.com/auth/mfa",                 service_id=auth.id),

        # API Gateway
        Doc(title="API Gateway Rate Limiting Config",    url="https://docs.acme.com/gateway/rate-limiting",    service_id=gateway.id),

        # Notifications
        Doc(title="Notification Service API Reference",  url="https://docs.acme.com/notifications/api",        service_id=notifications.id),

        # Search
        Doc(title="Search Index Schema & Query Guide",   url="https://docs.acme.com/search/index-schema",      service_id=search.id),

        # Monitoring
        Doc(title="Alerting & On-Call Runbook",          url="https://docs.acme.com/monitoring/on-call",       service_id=monitoring.id),
    ]

    db.add_all(docs)
    db.commit()
    db.close()

    print(f"Database seeded: 8 team members, 10 services, {len(docs)} docs.")


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    seed(reset=reset)
