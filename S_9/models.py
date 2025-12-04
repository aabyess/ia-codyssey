# models.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, default=datetime.utcnow)

    # 관계: 1:N (질문 → 답변들)
    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, default=datetime.utcnow)

    question_id = Column(Integer, ForeignKey("question.id", ondelete="CASCADE"))
    question = relationship("Question", back_populates="answers")
