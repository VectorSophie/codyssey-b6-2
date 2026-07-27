"""라우터 계층: 요청을 받아 서비스에 위임하고, 결과를 템플릿 또는 리다이렉트로 돌려준다."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from services import memo_service
from services.memo_service import MemoNotFoundError

router = APIRouter(prefix="/memos")
templates = Jinja2Templates(directory="templates")


@router.get("")
def list_memos(request: Request, db: Session = Depends(get_db)):
    memos = memo_service.list_memos(db)
    return templates.TemplateResponse(request, "list.html", {"memos": memos})


@router.get("/new")
def new_memo_form(request: Request):
    return templates.TemplateResponse(request, "form.html", {"memo": None})


@router.post("")
def create_memo(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    memo = memo_service.create_memo(db, title, content)
    return RedirectResponse(url=f"/memos/{memo.id}", status_code=303)


@router.get("/{memo_id}")
def memo_detail(request: Request, memo_id: int, db: Session = Depends(get_db)):
    try:
        memo = memo_service.get_memo(db, memo_id)
    except MemoNotFoundError:
        return templates.TemplateResponse(request, "not_found.html", status_code=404)
    return templates.TemplateResponse(request, "detail.html", {"memo": memo})


@router.get("/{memo_id}/edit")
def edit_memo_form(request: Request, memo_id: int, db: Session = Depends(get_db)):
    try:
        memo = memo_service.get_memo(db, memo_id)
    except MemoNotFoundError:
        return templates.TemplateResponse(request, "not_found.html", status_code=404)
    return templates.TemplateResponse(request, "form.html", {"memo": memo})


@router.post("/{memo_id}/edit")
def update_memo(
    request: Request,
    memo_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        memo_service.update_memo(db, memo_id, title, content)
    except MemoNotFoundError:
        return templates.TemplateResponse(request, "not_found.html", status_code=404)
    return RedirectResponse(url=f"/memos/{memo_id}", status_code=303)


@router.post("/{memo_id}/delete")
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    try:
        memo_service.delete_memo(db, memo_id)
    except MemoNotFoundError:
        pass
    return RedirectResponse(url="/memos", status_code=303)
