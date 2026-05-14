from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    text = Column(Text, nullable=False)
    question_type = Column(Enum("multiple_choice", "true_false"), default="multiple_choice", nullable=False)
    option_a = Column(String(500), nullable=True)
    option_b = Column(String(500), nullable=True)
    option_c = Column(String(500), nullable=True)
    option_d = Column(String(500), nullable=True)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, D or T, F
    points = Column(Integer, default=1)

    # Relationships
    exam = relationship("Exam", back_populates="questions")
    student_answers = relationship("StudentAnswer", back_populates="question", cascade="all, delete-orphan")
