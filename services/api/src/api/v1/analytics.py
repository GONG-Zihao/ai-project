from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.user import User
from ...db.session import get_db
from ...services.learning_service import learning_service
from ..deps import get_current_user

router = APIRouter()


@router.get("/progress")
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    metrics = await learning_service.user_progress_metrics(db, user_id=current_user.id)
    overview = await learning_service.classroom_overview(db, user_id=current_user.id)
    return {"metrics": metrics, "overview": overview}


@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    achievements = await learning_service.achievements_for_user(db, user_id=current_user.id)
    return achievements
