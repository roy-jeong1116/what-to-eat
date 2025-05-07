from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from notifications import notify_expiring_items

from domain.user import user_router
from domain.item import item_router
from domain.ocr.ocr_router import router as ocr_router

# 1) 스케줄러 인스턴스 생성
scheduler = AsyncIOScheduler()

# 2) Lifespan 이벤트 핸들러 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup logic ---
    # 매일 오후 18:00에 알림 작업 실행
    scheduler.add_job(notify_expiring_items, 'cron', hour=18, minute=0)
    scheduler.start()

    yield  # 여기서 FastAPI가 “running” 상태로 전환됩니다

    # --- shutdown logic ---
    scheduler.shutdown()

# 3) FastAPI 앱 생성 시 lifespan 파라미터로 전달
app = FastAPI(lifespan=lifespan)

app.include_router(user_router.router,   tags=["User"])
app.include_router(item_router.router,   tags=["Item"])
app.include_router(ocr_router,           tags=["OCR"])