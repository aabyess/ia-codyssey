from __future__ import annotations

import json
from typing import Dict, Any, Optional
from urllib import request, error

BASE_URL: str = 'http://127.0.0.1:8000/api'  # 메모: 서버 기본 주소


def call_api(method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """메모: 공통 HTTP 호출 함수 (JSON 입출력)."""
    url = f'{BASE_URL}{path}'
    body = None
    headers = {'Content-Type': 'application/json'}

    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')

    req = request.Request(url=url, data=body, method=method, headers=headers)

    try:
        with request.urlopen(req) as resp:
            text = resp.read().decode('utf-8')
            if not text:
                return {}
            return json.loads(text)
    except error.HTTPError as exc:
        return {'error': f'HTTP {exc.code}', 'detail': exc.read().decode('utf-8', errors='ignore')}
    except Exception as exc:  # noqa: BLE001
        return {'error': type(exc).__name__, 'detail': str(exc)}


def print_json(title: str, data: Dict[str, Any]) -> None:
    """메모: JSON 응답을 보기 좋게 출력."""
    print(f'\n[{title}]')
    print(json.dumps(data, indent=2, ensure_ascii=False))


def action_list_all() -> None:
    """메모: 전체 TO-DO 목록 조회."""
    res = call_api('GET', '/todos')
    print_json('전체 조회 결과', res)


def action_get_single() -> None:
    """메모: 개별 TO-DO 조회."""
    raw = input('조회할 id를 입력하세요: ').strip()
    if not raw.isdigit():
        print('id는 정수여야 합니다.')
        return
    item_id = int(raw)
    res = call_api('GET', f'/todos/{item_id}')
    print_json('개별 조회 결과', res)


def action_add() -> None:
    """메모: 새 TO-DO 추가."""
    title = input('제목(title)을 입력하세요: ').strip()
    priority = input('우선순위(priority)를 입력하세요 (예: high/low): ').strip()

    payload: Dict[str, Any] = {}
    if title:
        payload['title'] = title
    if priority:
        payload['priority'] = priority

    res = call_api('POST', '/add_todo', payload)
    print_json('추가 결과', res)


def action_update() -> None:
    """메모: 기존 TO-DO 수정."""
    raw = input('수정할 id를 입력하세요: ').strip()
    if not raw.isdigit():
        print('id는 정수여야 합니다.')
        return
    item_id = int(raw)

    print('변경할 필드를 입력하세요. 빈 값으로 두면 해당 필드는 건너뜁니다.')
    new_title = input('새 제목(title): ').strip()
    new_priority = input('새 우선순위(priority): ').strip()
    new_done = input('완료 여부(done, true/false 중 하나): ').strip().lower()

    fields: Dict[str, Any] = {}
    if new_title:
        fields['title'] = new_title
    if new_priority:
        fields['priority'] = new_priority
    if new_done in ('true', 'false'):
        fields['done'] = new_done == 'true'

    if not fields:
        print('변경할 내용이 없습니다.')
        return

    # 메모: 서버측 TodoItem 모델 규격에 맞게 감싸서 전송
    payload = {'fields': fields}
    res = call_api('PUT', f'/todos/{item_id}', payload)
    print_json('수정 결과', res)


def action_delete() -> None:
    """메모: 기존 TO-DO 삭제."""
    raw = input('삭제할 id를 입력하세요: ').strip()
    if not raw.isdigit():
        print('id는 정수여야 합니다.')
        return
    item_id = int(raw)

    res = call_api('DELETE', f'/todos/{item_id}')
    print_json('삭제 결과', res)


def main_menu() -> None:
    """메모: 메인 메뉴 루프."""
    while True:
        print('\n===== TODO 클라이언트 앱 =====')
        print('1. 전체 TO-DO 조회')
        print('2. 개별 TO-DO 조회')
        print('3. TO-DO 추가')
        print('4. TO-DO 수정')
        print('5. TO-DO 삭제')
        print('0. 종료')
        choice = input('메뉴 번호를 선택하세요: ').strip()

        if choice == '1':
            action_list_all()
        elif choice == '2':
            action_get_single()
        elif choice == '3':
            action_add()
        elif choice == '4':
            action_update()
        elif choice == '5':
            action_delete()
        elif choice == '0':
            print('클라이언트 앱을 종료합니다.')
            break
        else:
            print('올바른 메뉴 번호를 선택하세요.')


if __name__ == '__main__':
    # 메모: 프로그램 시작점
    main_menu()
