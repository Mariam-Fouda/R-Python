from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from app.models.result import StudentAnswer, Result
from app.models.exam import Exam
from app.models.question import Question
from app.schemas.result import ExamSubmission
from app.core.cache import get_cache, set_cache, delete_pattern
from app.core.logger import logger


def submit_exam(db: Session, submission: ExamSubmission, student_id: int) -> Result:
    # Check exam exists and is active
    exam = db.query(Exam).filter(Exam.id == submission.exam_id, Exam.is_active == True).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found or not active")

    # Check if student already submitted
    existing = db.query(Result).filter(
        Result.student_id == student_id,
        Result.exam_id == submission.exam_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted this exam")

    # Grade answers
    total_points = 0
    earned_points = 0
    answer_records = []

    for answer in submission.answers:
        question = db.query(Question).filter(
            Question.id == answer.question_id,
            Question.exam_id == submission.exam_id
        ).first()
        if not question:
            continue

        total_points += question.points
        is_correct = answer.selected_answer.upper() == question.correct_answer.upper()
        if is_correct:
            earned_points += question.points

        student_answer = StudentAnswer(
            student_id=student_id,
            question_id=answer.question_id,
            exam_id=submission.exam_id,
            selected_answer=answer.selected_answer.upper(),
            is_correct=is_correct,
        )
        answer_records.append(student_answer)

    # Save answers
    for record in answer_records:
        db.add(record)

    # Calculate results
    percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    passed = percentage >= 50.0

    result = Result(
        student_id=student_id,
        exam_id=submission.exam_id,
        score=float(earned_points),
        total_points=total_points,
        earned_points=earned_points,
        percentage=percentage,
        passed=passed,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    delete_pattern(f"results:student:{student_id}:*")
    logger.info(f"Exam submitted: student={student_id}, exam={submission.exam_id}, score={percentage:.1f}%")
    return result


def get_student_results(db: Session, student_id: int) -> list:
    cache_key = f"results:student:{student_id}:all"
    cached = get_cache(cache_key)
    if cached:
        return cached

    results = db.query(Result).filter(Result.student_id == student_id).all()
    data = []
    for r in results:
        data.append({
            "id": r.id,
            "student_id": r.student_id,
            "exam_id": r.exam_id,
            "exam_title": r.exam.title if r.exam else None,
            "score": r.score,
            "total_points": r.total_points,
            "earned_points": r.earned_points,
            "percentage": r.percentage,
            "passed": r.passed,
            "completed_at": str(r.completed_at),
        })
    set_cache(cache_key, data, ttl=120)
    return data


def get_result_detail(db: Session, result_id: int, student_id: int) -> dict:
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    if result.student_id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")

    answers = db.query(StudentAnswer).filter(
        StudentAnswer.student_id == student_id,
        StudentAnswer.exam_id == result.exam_id,
    ).all()

    answer_details = []
    for a in answers:
        answer_details.append({
            "question_id": a.question_id,
            "selected_answer": a.selected_answer,
            "correct_answer": a.question.correct_answer,
            "is_correct": a.is_correct,
            "points": a.question.points,
        })

    return {
        "id": result.id,
        "student_id": result.student_id,
        "exam_id": result.exam_id,
        "exam_title": result.exam.title if result.exam else None,
        "score": result.score,
        "total_points": result.total_points,
        "earned_points": result.earned_points,
        "percentage": result.percentage,
        "passed": result.passed,
        "completed_at": str(result.completed_at),
        "answers": answer_details,
    }


def get_exam_analytics(db: Session, exam_id: int) -> dict:
    cache_key = f"analytics:exam:{exam_id}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    results = db.query(Result).filter(Result.exam_id == exam_id).all()
    if not results:
        return {
            "exam_id": exam_id,
            "exam_title": exam.title,
            "total_attempts": 0,
            "average_score": 0,
            "average_percentage": 0,
            "pass_rate": 0,
            "highest_score": 0,
            "lowest_score": 0,
        }

    percentages = [r.percentage for r in results]
    passed_count = sum(1 for r in results if r.passed)

    analytics = {
        "exam_id": exam_id,
        "exam_title": exam.title,
        "total_attempts": len(results),
        "average_score": sum(r.score for r in results) / len(results),
        "average_percentage": sum(percentages) / len(percentages),
        "pass_rate": (passed_count / len(results)) * 100,
        "highest_score": max(percentages),
        "lowest_score": min(percentages),
    }
    set_cache(cache_key, analytics, ttl=60)
    return analytics


def get_all_results_admin(db: Session) -> list:
    cache_key = "results:admin:all"
    cached = get_cache(cache_key)
    if cached:
        return cached

    results = db.query(Result).all()
    data = []
    for r in results:
        data.append({
            "id": r.id,
            "student_id": r.student_id,
            "student_name": r.student.username if r.student else None,
            "exam_id": r.exam_id,
            "exam_title": r.exam.title if r.exam else None,
            "percentage": r.percentage,
            "passed": r.passed,
            "completed_at": str(r.completed_at),
        })
    set_cache(cache_key, data, ttl=60)
    return data
