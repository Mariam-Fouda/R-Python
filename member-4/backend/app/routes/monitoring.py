from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import require_admin
from app.core.cache import get_redis_info
from app.models.user import User
from app.models.exam import Exam
from app.models.result import Result
import os

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "Online Examination System"}


@router.get("/stats")
def system_stats(db: Session = Depends(get_db), admin=Depends(require_admin)):
    total_users = db.query(func.count(User.id)).scalar()
    total_students = db.query(func.count(User.id)).filter(User.role == "student").scalar()
    total_admins = db.query(func.count(User.id)).filter(User.role == "admin").scalar()
    total_exams = db.query(func.count(Exam.id)).scalar()
    active_exams = db.query(func.count(Exam.id)).filter(Exam.is_active == True).scalar()
    total_submissions = db.query(func.count(Result.id)).scalar()
    passed_submissions = db.query(func.count(Result.id)).filter(Result.passed == True).scalar()

    redis_info = get_redis_info()

    return {
        "users": {
            "total": total_users,
            "students": total_students,
            "admins": total_admins,
        },
        "exams": {
            "total": total_exams,
            "active": active_exams,
        },
        "submissions": {
            "total": total_submissions,
            "passed": passed_submissions,
            "failed": total_submissions - passed_submissions,
            "pass_rate": round((passed_submissions / total_submissions * 100), 1) if total_submissions > 0 else 0,
        },
        "redis": redis_info,
    }


@router.get("/logs")
def get_recent_logs(admin=Depends(require_admin)):
    log_path = "/app/logs/app.log"
    if not os.path.exists(log_path):
        return {"logs": []}
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
        recent = lines[-100:] if len(lines) > 100 else lines
        return {"logs": [line.strip() for line in recent]}
    except Exception as e:
        return {"logs": [], "error": str(e)}
