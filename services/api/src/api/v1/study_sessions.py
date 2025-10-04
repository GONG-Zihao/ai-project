from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.user import User
from ...db.session import get_db
from ...repositories import study_sessions as study_repo
from ...repositories import audit as audit_repo
from ...schemas.study import StudySessionCreate, StudySessionRead
from ..deps import get_current_user

router = APIRouter()


@router.post("", response_model=StudySessionRead)
async def create_study_session(
    payload: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudySessionRead:
    start_at = payload.start_at or datetime.utcnow()
    session = await study_repo.create(
        db,
        user_id=current_user.id,
        start_at=start_at,
        end_at=payload.end_at,
        duration_hours=payload.duration_hours,
        device=payload.device,
    )
    await audit_repo.log_event(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="create",
        resource="study_session",
        metadata={"session_id": session.id},
    )
    return StudySessionRead.model_validate(session)


@router.get("", response_model=list[StudySessionRead])
async def list_study_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[StudySessionRead]:
    sessions = await study_repo.list_for_user(db, user_id=current_user.id)
    return [StudySessionRead.model_validate(session) for session in sessions]
