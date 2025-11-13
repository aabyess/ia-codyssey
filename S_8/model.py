# 메모: 수정(PUT) 시 전달할 자유 형식의 키-값 페이로드 모델

from typing import Dict, Any
from pydantic import BaseModel


class TodoItem(BaseModel):
    # 메모: 수정할 필드들을 한꺼번에 전달 (예: {"priority": "low", "done": True})
    fields: Dict[str, Any]
