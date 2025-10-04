from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import api_router
from .core.config import settings
from .core.logging import setup_logging
from .db.session import engine, Base, AsyncSessionLocal
from .repositories import users as user_repo

app = FastAPI(title=settings.app_name, debug=settings.app_debug)

setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    return response


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await user_repo.ensure_default_admin(session)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


app.include_router(api_router, prefix="/api/v1")
