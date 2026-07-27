from fastapi import FastAPI

from database import Base, engine
from models import memo  # noqa: F401  (모델을 import해야 create_all이 테이블을 인식한다)
from routers import home, memo as memo_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="메모장")
app.include_router(home.router)
app.include_router(memo_router.router)
