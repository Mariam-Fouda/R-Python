from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse, ExamDetailResponse
from app.services.exam_service import (
    create_exam, get_all_exams, get_exam_by_id, update_exam, delete_exam
)

router = APIRouter(prefix="/api/exams", tags=["Exams"])


@router.post("/", status_code=201)
def create(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    exam = create_exam(db, exam_data, admin.id)
    return {"message": "Exam created successfully", "exam_id": exam.id}


@router.get("/")
def list_exams(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_all_exams(db)


@router.get("/{exam_id}")
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_exam_by_id(db, exam_id)


@router.put("/{exam_id}")
def update(
    exam_id: int,
    exam_data: ExamUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    exam = update_exam(db, exam_id, exam_data)
    return {"message": "Exam updated", "exam_id": exam.id}


@router.delete("/{exam_id}")
def delete(
    exam_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    delete_exam(db, exam_id)
    return {"message": "Exam deleted"}
