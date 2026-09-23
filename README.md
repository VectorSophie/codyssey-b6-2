# b6-2 — FastAPI 메모장 (라우터/서비스/저장소 계층 분리 + PRG)

FastAPI + SQLAlchemy + Jinja2 SSR로 만든 메모 CRUD 웹앱입니다. 인메모리가 아니라 SQLite DB에 저장되고, 등록/수정/삭제 후에는 항상 303 리다이렉트로 새로고침 중복 제출을 막습니다.

## 개발 환경

- Python 3.10 이상 (개발/검증은 3.12에서 진행)
- 패키지: `fastapi`, `uvicorn`, `sqlalchemy`, `jinja2`, `python-multipart` (requirements.txt에 고정, 이 범위 밖 라이브러리는 추가하지 않았습니다)

## 실행 방법

```sh
cd codyssey-b6-2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

`http://localhost:8000` 접속. 실행하면 같은 폴더에 `database.db`(SQLite)가 자동 생성됩니다.

## 폴더 구조

```
codyssey-b6-2/
├── main.py              # FastAPI 앱 생성 + 라우터 등록 + 테이블 생성
├── database.py           # engine/SessionLocal/get_db 의존성
├── models/memo.py        # SQLAlchemy ORM 모델 (Memo)
├── repositories/memo_repository.py  # DB 접근만 (Session 쿼리)
├── services/memo_service.py         # 비즈니스 로직 (존재 확인, 공백 정리 등)
├── routers/home.py, routers/memo.py # 요청/응답, 템플릿 렌더링, 리다이렉트
├── templates/            # base/home/list/detail/form/not_found
└── test_app.py           # self-check (실제 서버를 띄워 CRUD 흐름 검증)
```

## 도메인 선택

메모(제목/내용/작성일시) — requirements.md에 예시로 나온 것 중 가장 단순해서 골랐습니다. 라우터→서비스→저장소→템플릿 흐름을 보여주는 게 목적이라 도메인 자체는 복잡할 필요가 없었습니다.

## 화면 흐름

| 화면 | 경로 | 메서드 |
|---|---|---|
| 홈 | `/` | GET |
| 목록 | `/memos` | GET |
| 상세 | `/memos/{id}` | GET |
| 새 메모 폼 | `/memos/new` | GET |
| 등록 처리 | `/memos` | POST → 303 → `/memos/{id}` |
| 수정 폼 | `/memos/{id}/edit` | GET |
| 수정 처리 | `/memos/{id}/edit` | POST → 303 → `/memos/{id}` |
| 삭제 처리 | `/memos/{id}/delete` | POST → 303 → `/memos` |

존재하지 않는 id로 상세/수정에 접근하면 404 + "해당 데이터를 찾을 수 없습니다" 화면을 보여줍니다.

## self-check

```sh
python3 test_app.py
```

`test_run_database.db`라는 별도 SQLite 파일로 실제 uvicorn 서버를 띄운 뒤, 등록→목록→상세→수정→404→삭제까지 순서대로 HTTP 요청을 보내 검증합니다. 끝나면 서버를 종료하고 테스트 DB 파일을 지웁니다.

## 스킵한 것

- 입력값 서버사이드 검증(빈 제목 등)은 보너스 항목이라 HTML `required` 속성으로만 처리했습니다. 서버단 검증이 필요하면 `services/memo_service.py`에 한 줄 가드 추가하면 됩니다.
- 검색/필터도 보너스라 넣지 않았습니다.
