"""데이터 접근 계층. Session을 통한 Memo CRUD만 담당하고 비즈니스 판단은 하지 않는다."""
from sqlalchemy.orm import Session

from models.memo import Memo


def get_all(db: Session) -> list[Memo]:
    return db.query(Memo).order_by(Memo.created_at.desc()).all()


def get_by_id(db: Session, memo_id: int) -> Memo | None:
    return db.query(Memo).filter(Memo.id == memo_id).first()


def create(db: Session, title: str, content: str) -> Memo:
    memo = Memo(title=title, content=content)
    db.add(memo)
    db.commit()
    db.refresh(memo)
    return memo


def update(db: Session, memo: Memo, title: str, content: str) -> Memo:
    memo.title = title
    memo.content = content
    db.commit()
    db.refresh(memo)
    return memo


def delete(db: Session, memo: Memo) -> None:
    db.delete(memo)
    db.commit()
