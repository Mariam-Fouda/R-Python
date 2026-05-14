from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.result import ExamSubmission
from app.services.result_service import (
    submit_exam, get_student_results, get_result_detail,
    get_exam_analytics, get_all_results_admin
)

router = APIRouter(prefix="/api/results", tags=["Results"])


@router.post("/submit")
def submit(
    submission: ExamSubmission,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = submit_exam(db, submission, current_user.id)
    return {
        "message": "Exam submitted successfully",
        "result_id": result.id,
        "percentage": result.percentage,
        "passed": result.passed,
        "earned_points": result.earned_points,
        "total_points": result.total_points,
    }


@router.get("/my")
def my_results(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_student_results(db, current_user.id)


@router.get("/my/{result_id}")
def result_detail(
    result_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_result_detail(db, result_id, current_user.id)


@router.get("/admin/all")
def all_results(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return get_all_results_admin(db)


@router.get("/analytics/{exam_id}")
def analytics(
    exam_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return get_exam_analytics(db, exam_id)
