from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.user import User, UserRole
from ...db.session import get_db
from ...repositories import interactions as interaction_repo
from ...repositories import audit as audit_repo
from ...services.ai_service import ai_service
from ...schemas.qa import LessonPlanRequest, LessonPlanResponse, QARequest, QAResponse
from ..deps import get_current_user, require_roles

router = APIRouter()


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    payload: QARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QAResponse:
    result = await ai_service.answer_question(
        question=payload.question,
        subject=payload.subject,
        user_context=payload.user_context,
    )
    await interaction_repo.create(
        db,
        user_id=current_user.id,
        subject=payload.subject,
        prompt=payload.question,
        response=result["answer"],
        provider=result["provider"],
        latency_ms=None,
        metadata={"citations": result["citations"], "usage": result["usage"]},
    )
    await audit_repo.log_event(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="ask",
        resource="qa",
        metadata={"subject": payload.subject},
    )
    return QAResponse(**result)


@router.post("/lesson-plan", response_model=LessonPlanResponse)
async def generate_lesson_plan(
    payload: LessonPlanRequest,
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> LessonPlanResponse:
    result = await ai_service.generate_lesson_plan(
        subject=payload.subject,
        topic=payload.topic,
        objectives=payload.objectives,
        audience=payload.audience,
    )
    await audit_repo.log_event(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="generate_lesson_plan",
        resource="qa",
        metadata={"subject": payload.subject, "topic": payload.topic},
    )
    return LessonPlanResponse(**result)
