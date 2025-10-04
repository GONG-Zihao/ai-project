from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.user import User
from ...db.session import get_db
from ...repositories import mistakes as mistakes_repo
from ...repositories import knowledge as knowledge_repo
from ...services.learning_service import learning_service
from ...schemas.knowledge import KnowledgePointRead
from ..deps import get_current_user

router = APIRouter()


@router.get("/plan")
async def get_learning_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    mistakes = await mistakes_repo.list_for_user(db, user_id=current_user.id)
    plan = learning_service.generate_learning_plan(mistakes)
    return {"plan": plan}


@router.get("/knowledge")
async def get_knowledge_mastery(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    subject: str | None = None,
) -> dict:
    await learning_service.update_knowledge_mastery(db, user_id=current_user.id, tenant_id=current_user.tenant_id)
    knowledge = await knowledge_repo.list_for_tenant(db, tenant_id=current_user.tenant_id, subject=subject)
    return {"knowledge": [KnowledgePointRead.model_validate(k) for k in knowledge]}


@router.get("/overview")
async def get_learning_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    overview = await learning_service.classroom_overview(db, user_id=current_user.id)
    return {"overview": overview}
