from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.user import User
from ...db.session import get_db
from ...repositories import mistakes as mistakes_repo
from ...repositories import audit as audit_repo
from ...schemas.mistake import MistakeCreate, MistakeRead
from ..deps import get_current_user

router = APIRouter()


@router.post("", response_model=MistakeRead, status_code=status.HTTP_201_CREATED)
async def create_mistake(
    payload: MistakeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MistakeRead:
    mistake = await mistakes_repo.create(
        db,
        user_id=current_user.id,
        problem_id=payload.problem_id,
        subject=payload.subject,
        knowledge_tags=payload.knowledge_tags,
        difficulty=payload.difficulty,
        notes=payload.notes,
        metadata=payload.metadata,
    )
    await audit_repo.log_event(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="create",
        resource="mistake",
        metadata={"mistake_id": mistake.id},
    )
    return MistakeRead.model_validate(mistake)


@router.get("", response_model=list[MistakeRead])
async def list_mistakes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MistakeRead]:
    mistakes = await mistakes_repo.list_for_user(db, user_id=current_user.id)
    return [MistakeRead.model_validate(m) for m in mistakes]
