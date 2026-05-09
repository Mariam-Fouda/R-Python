from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.exam import Exam
from app.models.question import Question
from app.schemas.exam import ExamCreate, ExamUpdate
from app.core.cache import get_cache, set_cache, delete_pattern
from app.core.logger import logger


def create_exam(db: Session, exam_data: ExamCreate, admin_id: int) -> Exam:
    exam = Exam(
        title=exam_data.title,
        description=exam_data.description,
        duration_minutes=exam_data.duration_minutes,
        created_by_id=admin_id,
    )
    db.add(exam)
    db.flush()  # get exam.id

    for q_data in exam_data.questions:
        question = Question(
            exam_id=exam.id,
            text=q_data.text,
            question_type=q_data.question_type,
            option_a=q_data.option_a,
            option_b=q_data.option_b,
            option_c=q_data.option_c,
            option_d=q_data.option_d,
            correct_answer=q_data.correct_answer.upper(),
            points=q_data.points,
        )
        db.add(question)

    db.commit()
    db.refresh(exam)
    delete_pattern("exams:*")
    logger.info(f"Exam created: {exam.title} (id={exam.id})")
    return exam


def get_all_exams(db: Session) -> list:
    cache_key = "exams:all"
    cached = get_cache(cache_key)
    if cached:
        return cached

    exams = db.query(Exam).filter(Exam.is_active == True).all()
    result = []
    for e in exams:
        result.append({
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "duration_minutes": e.duration_minutes,
            "is_active": e.is_active,
            "created_by_id": e.created_by_id,
            "created_at": str(e.created_at),
            "question_count": len(e.questions),
        })
    set_cache(cache_key, result)
    return result


def get_exam_by_id(db: Session, exam_id: int, include_answers: bool = False) -> Exam:
    cache_key = f"exams:{exam_id}"
    if not include_answers:
        cached = get_cache(cache_key)
        if cached:
            return cached

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if not include_answers:
        result = {
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "duration_minutes": exam.duration_minutes,
            "is_active": exam.is_active,
            "created_by_id": exam.created_by_id,
            "created_at": str(exam.created_at),
            "question_count": len(exam.questions),
            "questions": [
                {
                    "id": q.id,
                    "exam_id": q.exam_id,
                    "text": q.text,
                    "question_type": q.question_type,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "points": q.points,
                }
                for q in exam.questions
            ],
        }
        set_cache(cache_key, result)
        return result

    return exam


def update_exam(db: Session, exam_id: int, exam_data: ExamUpdate) -> Exam:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    for field, value in exam_data.model_dump(exclude_unset=True).items():
        setattr(exam, field, value)

    db.commit()
    db.refresh(exam)
    delete_pattern("exams:*")
    logger.info(f"Exam updated: id={exam_id}")
    return exam


def delete_exam(db: Session, exam_id: int):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    db.delete(exam)
    db.commit()
    delete_pattern("exams:*")
    logger.info(f"Exam deleted: id={exam_id}")
