# 메모: FastAPI TO-DO API (CSV 저장) — 추가/조회/개별조회/수정/삭제

from __future__ import annotations

from fastapi import FastAPI, APIRouter, Body
from typing import Dict, List, Any, Optional
import csv
import json
import os
import threading

from model import TodoItem  # 메모: 수정용 모델

# 메모: 전역 상수/상태
CSV_PATH: str = 'todo.csv'                 # 메모: TO-DO 데이터를 저장할 CSV 경로
CSV_FIELDS: List[str] = ['id', 'payload']  # 메모: id, payload(JSON 문자열) 2개 컬럼
todo_list: List[Dict[str, Any]] = []       # 메모: 메모리에 유지할 TO-DO 목록
_id_lock = threading.Lock()                # 메모: 동시성 보호용 락 (id/CSV 보호)
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
                obj: Dict[str, Any] = {'id': item_id, **payload}  # 메모: id 병합
                loaded.append(obj)
                if item_id > max_id:
                    max_id = item_id
            except (ValueError, KeyError, json.JSONDecodeError):
                # 메모: 손상된 행은 무시 (조용히 스킵)
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


def _rewrite_csv_from_memory() -> None:
    """메모: 메모리에 있는 todo_list 전체를 CSV로 재작성."""
    _ensure_csv_initialized()
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for item in todo_list:
            item_id = int(item.get('id'))
            payload = {k: v for k, v in item.items() if k != 'id'}
            writer.writerow({
                'id': item_id,
                'payload': json.dumps(payload, ensure_ascii=False),
            })


def _find_index_by_id(item_id: int) -> Optional[int]:
    """메모: id로 리스트 인덱스 찾기 (없으면 None)."""
    for idx, item in enumerate(todo_list):
        if item.get('id') == item_id:
            return idx
    return None


@router.post('/add_todo')
def add_todo(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """메모: 새 TO-DO 추가 (POST), 입력이 빈 Dict면 경고 반환(보너스)."""
    if not isinstance(payload, dict):
        return {'warning': '입력은 Dict 타입이어야 합니다.'}
    if len(payload) == 0:
        return {'warning': '입력 Dict가 비어 있습니다. 항목을 추가해 주세요.'}

    with _id_lock:
        global _next_id
        item_id = _next_id
        _next_id += 1

        item = {'id': item_id, **payload}  # 메모: 메모리에는 id 병합
        todo_list.append(item)
        _append_to_csv(item_id, payload)   # 메모: CSV에는 JSON payload로 저장

    return {'result': 'ok', 'id': item_id}


@router.get('/todos')
def retrieve_todo() -> Dict[str, Any]:
    """메모: 전체 TO-DO 목록 반환 (GET)."""
    return {'todos': todo_list}


@router.get('/todos/{item_id}')
def get_single_todo(item_id: int) -> Dict[str, Any]:
    """메모: 개별 TO-DO 조회 (GET)."""
    idx = _find_index_by_id(item_id)
    if idx is None:
        return {'warning': f'id={item_id} 항목이 없습니다.'}
    return {'todo': todo_list[idx]}


@router.put('/todos/{item_id}')
def update_todo(item_id: int, item: TodoItem) -> Dict[str, Any]:
    """메모: 개별 TO-DO 수정 (PUT, 모델 사용)."""
    idx = _find_index_by_id(item_id)
    if idx is None:
        return {'warning': f'id={item_id} 항목이 없습니다.'}

    with _id_lock:
        # 메모: 기존 payload(= id 제외)와 새로운 fields 병합(덮어쓰기)
        current = todo_list[idx]
        base_payload = {k: v for k, v in current.items() if k != 'id'}
        merged = {**base_payload, **item.fields}
        todo_list[idx] = {'id': item_id, **merged}
        _rewrite_csv_from_memory()

    return {'result': 'ok', 'updated': todo_list[idx]}


@router.delete('/todos/{item_id}')
def delete_single_todo(item_id: int) -> Dict[str, Any]:
    """메모: 개별 TO-DO 삭제 (DELETE)."""
    idx = _find_index_by_id(item_id)
    if idx is None:
        return {'warning': f'id={item_id} 항목이 없습니다.'}

    with _id_lock:
        todo_list.pop(idx)
        _rewrite_csv_from_memory()

    return {'result': 'ok', 'deleted_id': item_id}


app = FastAPI(title='Simple TODO with FastAPI (CSV)')
app.include_router(router)


@app.on_event('startup')
def on_startup() -> None:
    """메모: 서버 시작 시 CSV 로드."""
    _load_from_csv()
