from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AnswerSubmit(BaseModel):
    question_id: int
    selected_answer: str  # A, B, C, D or T, F


class ExamSubmission(BaseModel):
    exam_id: int
    answers: List[AnswerSubmit]


class AnswerResult(BaseModel):
    question_id: int
    selected_answer: str
    correct_answer: str
    is_correct: bool
    points: int


class ResultResponse(BaseModel):
    id: int
    student_id: int
    exam_id: int
    exam_title: Optional[str] = None
    score: float
    total_points: int
    earned_points: int
    percentage: float
    passed: bool
    completed_at: datetime
    answers: Optional[List[AnswerResult]] = None

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    exam_id: int
    exam_title: str
    total_attempts: int
    average_score: float
    average_percentage: float
    pass_rate: float
    highest_score: float
    lowest_score: float
