"""비즈니스 로직 계층. 라우터는 이 함수들만 호출하고 DB를 직접 만지지 않는다."""
from sqlalchemy.orm import Session

from models.memo import Memo
from repositories import memo_repository


class MemoNotFoundError(Exception):
    """존재하지 않는 memo_id 접근 시 발생."""


def list_memos(db: Session) -> list[Memo]:
    return memo_repository.get_all(db)


def get_memo(db: Session, memo_id: int) -> Memo:
    memo = memo_repository.get_by_id(db, memo_id)
    if memo is None:
        raise MemoNotFoundError(memo_id)
    return memo


def create_memo(db: Session, title: str, content: str) -> Memo:
    return memo_repository.create(db, title=title.strip(), content=content.strip())


def update_memo(db: Session, memo_id: int, title: str, content: str) -> Memo:
    memo = get_memo(db, memo_id)
    return memo_repository.update(db, memo, title=title.strip(), content=content.strip())


def delete_memo(db: Session, memo_id: int) -> None:
    memo = get_memo(db, memo_id)
    memo_repository.delete(db, memo)
