from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.agents.router import public_router as agents_public_router
from app.agents.router import router as agents_router
from app.auth_api.router import router as auth_router
from app.candidates.router import router as candidates_router
from app.config import get_settings
from app.database import Base, engine, get_db
from app.devseed import seed_demo_tenant
from app.health import build_health, build_ready
from app.invite_codes.router import router as invite_router
from app.jobs.router import router as jobs_router
from app.matching.router import router as matches_router
from app.matching.router import structure_router as ai_structure_router
from app.production_guards import ProductionGuardError, assert_hosted_safe
from app.talent_sourcing.router import router as source_router
import app.models  # noqa: F401 — register metadata for create_all


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    try:
        assert_hosted_safe(settings)
    except ProductionGuardError as exc:
        raise RuntimeError(str(exc)) from exc
    Base.metadata.create_all(bind=engine)
    seed_demo_tenant()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type", "X-Organization-Id", "X-Request-ID"],
    )
    app.include_router(auth_router)
    app.include_router(invite_router)
    app.include_router(jobs_router)
    app.include_router(candidates_router)
    app.include_router(source_router)
    app.include_router(matches_router)
    app.include_router(ai_structure_router)
    app.include_router(agents_router)
    app.include_router(agents_public_router)

    @app.get("/health")
    def health():
        return build_health(get_settings())

    @app.get("/ready")
    def ready(db: Session = Depends(get_db)):
        status_code, payload = build_ready(get_settings(), db)
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=status_code, content=payload)

    return app


app = create_app()
