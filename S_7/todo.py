from __future__ import annotations

from fastapi import FastAPI, APIRouter, Body
from typing import Dict, List, Any
import csv
import json
import os
import threading

# 메모: 전역 상수/상태
CSV_PATH: str = 'todo.csv'          # 메모: TO-DO 데이터를 저장할 CSV 경로
CSV_FIELDS: List[str] = ['id', 'payload']  # 메모: id, payload(JSON 문자열) 2개 컬럼
todo_list: List[Dict[str, Any]] = []       # 메모: 메모리에 유지할 TO-DO 목록
_id_lock = threading.Lock()                # 메모: 동시성 보호용 락 (id 발급/파일쓰기 보호)
_next_id: int = 1                          # 메모: 다음에 부여할 id 값 (CSV 로드시 갱신)

router = APIRouter(prefix='/api', tags=['todo'])  # 메모: APIRouter 사용 (요구사항)


def _ensure_csv_initialized() -> None:
    """메모: CSV 파일이 없으면 헤더와 함께 생성."""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def _load_from_csv() -> None:
    """메모: CSV에서 todo_list 로드 + _next_id 갱신."""
    global todo_list, _next_id
    _ensure_csv_initialized()
    loaded: List[Dict[str, Any]] = []
    max_id = 0

    with open(CSV_PATH, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                item_id = int(row['id'])
                payload = json.loads(row['payload'])
                # 메모: 클라이언트에 편하게 id 포함된 Dict로 제공
                obj: Dict[str, Any] = {'id': item_id, **payload}
                loaded.append(obj)
                if item_id > max_id:
                    max_id = item_id
            except (ValueError, KeyError, json.JSONDecodeError):
                # 메모: 손상된 행은 무시 (경고 없이 조용히 스킵)
                continue

    todo_list = loaded
    _next_id = max_id + 1 if max_id >= 1 else 1


def _append_to_csv(item_id: int, payload: Dict[str, Any]) -> None:
    """메모: 단일 항목을 CSV 끝에 추가."""
    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow({
            'id': item_id,
            'payload': json.dumps(payload, ensure_ascii=False),
        })


@router.post('/add_todo')
def add_todo(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """메모: 새 TO-DO 추가 (POST), 입력이 빈 Dict면 경고 반환(보너스)."""
    if not isinstance(payload, dict):
        return {'warning': '입력은 Dict 타입이어야 합니다.'}

    if len(payload) == 0:
        # 메모: 보너스 과제 — 빈 입력 경고
        return {'warning': '입력 Dict가 비어 있습니다. 항목을 추가해 주세요.'}

    # 메모: id 발급 + 메모리/CSV 동시 반영 (락으로 보호)
    with _id_lock:
        global _next_id
        item_id = _next_id
        _next_id += 1

        # 메모: 메모리 보관은 id를 병합한 Dict 형태로
        item = {'id': item_id, **payload}
        todo_list.append(item)

        # 메모: CSV에는 id, payload(JSON) 구조로 저장
        _append_to_csv(item_id, payload)

    return {'result': 'ok', 'id': item_id}


@router.get('/todos')
def retrieve_todo() -> Dict[str, Any]:
    """메모: 전체 TO-DO 목록 반환 (GET)."""
    # 메모: 응답도 Dict 타입으로 감싸서 반환
    return {'todos': todo_list}


app = FastAPI(title='Simple TODO with FastAPI (CSV)')
app.include_router(router)


@app.on_event('startup')
def on_startup() -> None:
    """메모: 서버 시작 시 CSV 로드."""
    _load_from_csv()
