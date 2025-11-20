from __future__ import annotations
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Text, DateTime, ForeignKey,)
from sqlalchemy.orm import relationship
from database import Base

class Question(Base):
    # 게시판의 질문 테이블
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True, index=True) # PK 지정 → 자동 증가되는 id 열이 됨.
    subject = Column(String(200), nullable=False)     # 질문 제목 최대길이, 비어있으면 안 됨
    content = Column(Text, nullable=False)            # 질문 내용 비어있으면 안 됨
    create_date = Column(DateTime, default=datetime.utcnow)  # DB에 넣을 때 자동으로 현재 UTC 시간 저장

    # 질문에 달린 답변 목록 (1:N 관계)
    answers = relationship('Answer', back_populates='question')


class Answer(Base):
    # 질문에 달린 답변 테이블
    __tablename__ = 'answer'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)          
    create_date = Column(DateTime, default=datetime.utcnow)  
    question_id = Column( 
        Integer,
        ForeignKey('question.id', ondelete='CASCADE'), # 외래키 설정
        nullable=False,
    )

    # 어느 질문에 달린 답변인지 (N:1 관계)
    question = relationship('Question', back_populates='answers')
