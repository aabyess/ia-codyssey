from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db_dep
from models import Question
from schemas import QuestionOut, QuestionCreate
from datetime import datetime

router = APIRouter(
    prefix="/api/question",
    tags=["Question"],
)


@router.get("/list", response_model=list[QuestionOut])
def question_list(db: Session = Depends(get_db_dep)):
    return db.query(Question).all()


@router.post("/create", response_model=QuestionOut)
def question_create(
    question_in: QuestionCreate,
    db: Session = Depends(get_db_dep)
):
    """
    메모: 새로운 질문을 SQLite DB에 저장한다.
    """
    new_question = Question(
        subject=question_in.subject,
        content=question_in.content,
        create_date=datetime.utcnow(),
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question
