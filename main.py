from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from domain.user import user_router
from domain.item import item_router
from domain.ocr.ocr_router import router as ocr_router
from domain.recipe_chatbot.chatbot_router import router as chatbot_router

app = FastAPI()

# CORS 미들웨어 설정
# 외부 도메인에서의 API 접근을 위한 보안 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 모든 출처에서의 요청 허용 (보안상 실제 서비스에서는 제한 필요)
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