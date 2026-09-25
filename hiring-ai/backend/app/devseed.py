DEMO_ORG_ID = "00000000-0000-4000-8000-000000000001"
DEMO_USER_ID = "00000000-0000-4000-8000-000000000002"


def seed_demo_tenant() -> None:
    from sqlalchemy import select

    from app.config import get_settings
    from app.database import SessionLocal
    from app.models import Membership, MembershipStatus, Organization, Role, Status, User

    settings = get_settings()
    if not settings.seed_demo_tenant or settings.auth_mode != "dev":
        return
    db = SessionLocal()
    try:
        if db.get(Organization, DEMO_ORG_ID) is None:
            db.add(Organization(id=DEMO_ORG_ID, name="Hiring AI Demo", slug="hiring-demo", status=Status.ACTIVE))
        if db.get(User, DEMO_USER_ID) is None:
            db.add(User(id=DEMO_USER_ID, email="demo@hiring.local", display_name="Demo Recruiter", status=Status.ACTIVE))
        db.flush()
        existing = db.scalar(
            select(Membership).where(
                Membership.org_id == DEMO_ORG_ID,
                Membership.user_id == DEMO_USER_ID,
            )
        )
        if existing is None:
            db.add(
                Membership(
                    org_id=DEMO_ORG_ID,
                    user_id=DEMO_USER_ID,
                    role=Role.OWNER,
                    status=MembershipStatus.ACTIVE,
                )
            )
        db.commit()
    finally:
        db.close()
