from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from domain.user import user_router
from domain.item import item_router
from domain.ocr.ocr_router import router as ocr_router

app = FastAPI()

app.include_router(user_router.router,   tags=["User"])
app.include_router(item_router.router,   tags=["Item"])
app.include_router(ocr_router,           tags=["OCR"])