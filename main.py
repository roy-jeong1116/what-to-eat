from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from domain.user import user_router
from domain.item import item_router

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(item_router.router)