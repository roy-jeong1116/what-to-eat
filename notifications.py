import os
import json

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import date, timedelta

import firebase_admin
from firebase_admin import credentials, initialize_app, messaging
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from models import User, Item

import config
import logging

# 1) Firebase Admin SDK 초기화 (중복 방지)
if not firebase_admin._apps:
    cred = credentials.Certificate(config.GOOGLE_APPLICATION_CREDENTIALS)
    initialize_app(cred)

logger = logging.getLogger(__name__)
router = APIRouter()

# 토큰 등록용 스키마/엔드포인트
class RegisterToken(BaseModel):
    user_id: int
    token: str

@router.post("/register-token")
def register_token(req: RegisterToken, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.fcm_token = req.token
    db.add(user)
    db.commit()
    return {"message": "Token registered."}

# 수동 푸시 발송용 스키마/엔드포인트
class PushRequest(BaseModel):
    token: str
    title: str
    body: str
    data: dict = None

@router.post("/push")
def push_message(req: PushRequest):
    message = messaging.Message(
        notification=messaging.Notification(title=req.title, body=req.body),
        token=req.token,
        data=req.data or {}
    )
    try:
        messaging.send(message)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}



# 알림 스케줄 함수 
def send_push_to_user(user: User, title: str, body: str, data: dict = None):
    token = user.fcm_token
    if not token or not user.notification:
        return
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data or {}
    )
    try:
        messaging.send(message)
    except Exception as e:
        logger.error(f"Failed to send FCM to user {user.user_id}: {e}")
        # 토큰 무효화 처리
        db: Session = SessionLocal()
        try:
            usr = db.query(User).get(user.user_id)
            usr.fcm_token = None
            db.add(usr)
            db.commit()
            logger.info(f"Cleared invalid token for user {user.user_id}")
        finally:
            db.close()

def notify_expiring_items():
    db = SessionLocal()
    try:
        today = date.today()
        # days 튜플로 수정: (3,) 혹은 (1,3,7) 등 원하는 일수
        for days in (3,):
            target = today + timedelta(days=days)
            items = db.query(Item).filter(Item.expiry_date == target).all()
            for item in items:
                user = item.user
                if not user.notification or not user.fcm_token:
                    continue
                title = f"[뭐먹을냉] 유통기한 알림"
                body  = f"{item.item_name}의 유통기한이 {target}까지 {days}일 남았습니다."
                send_push_to_user(user, title, body, {
                    "item_id": str(item.item_id),
                    "days": str(days)
                })
    finally:
        db.close()