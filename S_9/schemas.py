from pydantic import BaseModel, Field
from datetime import datetime


class QuestionCreate(BaseModel):
    subject: str = Field(..., min_length=1)   # 빈 값 허용 X
    content: str = Field(..., min_length=1)   # 빈 값 허용 X


class QuestionOut(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime

    class Config:
        orm_mode = True
