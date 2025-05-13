from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from notifications import notify_expiring_items
from sqlalchemy.orm import Session

from database import get_db

from domain.user import user_router
from domain.user import user_crud
from domain.item import item_router
from domain.qa import qa_router
from domain.ocr.ocr_router import router as ocr_router
from domain.recipe_chatbot.chatbot_router import router as chatbot_router

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

# CORS 미들웨어 설정
# 외부 도메인에서의 API 접근을 위한 보안 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],        # 모든 출처에서의 요청 허용 (보안상 실제 서비스에서는 제한 필요)
    allow_credentials=True,     # 쿠키 등 인증 정보 포함 요청 허용
    allow_methods=["*"],        # GET, POST, PUT, DELETE 등 모든 HTTP 메서드 허용
    allow_headers=["*"],        # 모든 요청 헤더 허용
    expose_headers=["*"],       # 클라이언트에게 노출할 응답 헤더 허용
)


# chatbot_router 안의 모든 엔드포인트를 OpenAPI 스키마에서 제외
for route in chatbot_router.routes:
    route.include_in_schema = False

app.include_router(user_router.router,   tags=["User"])
app.include_router(item_router.router,   tags=["Item"])
app.include_router(ocr_router,           tags=["OCR"])
app.include_router(chatbot_router, tags=["RecipeChatbot"])
app.include_router(qa_router.router)

@app.get("/{user_id}/mypage", tags=["MyPage"])
async def get_mypage(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_from_db(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
