from fastapi import APIRouter

from . import auth, learning, mistakes, qa, study_sessions, tenants, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(mistakes.router, prefix="/mistakes", tags=["mistakes"])
api_router.include_router(study_sessions.router, prefix="/study-sessions", tags=["study"])
api_router.include_router(qa.router, prefix="/qa", tags=["ai"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
