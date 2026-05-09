from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QuestionCreate(BaseModel):
    text: str
    question_type: str = "multiple_choice"  # multiple_choice or true_false
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: str  # A, B, C, D or T, F
    points: int = 1


class QuestionResponse(BaseModel):
    id: int
    exam_id: int
    text: str
    question_type: str
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    points: int

    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionResponse):
    correct_answer: str


class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int = 60
    questions: List[QuestionCreate] = []


class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class ExamResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    is_active: bool
    created_by_id: int
    created_at: datetime
    question_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ExamDetailResponse(ExamResponse):
    questions: List[QuestionResponse] = []
