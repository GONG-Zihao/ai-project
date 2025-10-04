from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.user import User, UserRole
from ...db.session import get_db
from ...repositories import classrooms as classroom_repo
from ...repositories import enrollments as enrollment_repo
from ...repositories import users as user_repo
from ...services.learning_service import learning_service
from ..deps import get_current_user, require_roles
from ...schemas.classroom import ClassroomCreate, ClassroomRead, EnrollmentRequest

router = APIRouter()


@router.post("/classrooms", response_model=ClassroomRead, status_code=status.HTTP_201_CREATED)
async def create_classroom(
    payload: ClassroomCreate,
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> ClassroomRead:
    teacher_id = payload.teacher_id or current_user.id
    classroom = await classroom_repo.create(
        db,
        tenant_id=current_user.tenant_id,
        name=payload.name,
        description=payload.description,
        teacher_id=teacher_id,
    )
    return ClassroomRead.model_validate(classroom)


@router.get("/classrooms", response_model=list[ClassroomRead])
async def list_classrooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ClassroomRead]:
    classrooms = await classroom_repo.list_for_tenant(db, tenant_id=current_user.tenant_id)
    return [ClassroomRead.model_validate(cls) for cls in classrooms]


@router.post("/classrooms/{classroom_id}/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_student(
    classroom_id: int,
    payload: EnrollmentRequest,
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    classroom = await classroom_repo.get_by_id(db, classroom_id)
    if classroom is None or classroom.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    target_user = await user_repo.get_by_id(db, payload.user_id)
    if target_user is None or target_user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or cross-tenant access denied")

    enrollment = await enrollment_repo.enroll(
        db,
        classroom_id=classroom_id,
        user_id=payload.user_id,
        role=payload.role,
    )
    return {"enrollment_id": enrollment.id}


@router.get("/classrooms/{classroom_id}/analytics")
async def classroom_analytics(
    classroom_id: int,
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    classroom = await classroom_repo.get_by_id(db, classroom_id)
    if classroom is None or classroom.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
    dashboard = await learning_service.classroom_dashboard(db, classroom_id=classroom_id)
    return dashboard
